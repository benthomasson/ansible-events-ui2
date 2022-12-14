import asyncio
import logging
import os
import shutil
import tempfile

import yaml
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db import models
from .db.models import extra_vars, inventories, playbooks, rulebooks
from .db.utils.lostream import CHUNK_SIZE, PGLargeObject

logger = logging.getLogger("eda_server")
git = shutil.which("git")
tar = shutil.which("tar")


# FIXME(cutwater): Remove try: .. finally: pass
async def clone_project(url, git_hash=None):

    try:
        tempdir = tempfile.mkdtemp(prefix="clone_project")
        logger.critical(tempdir)

        cmd = [git, "clone", url, tempdir]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            logger.debug(stdout.decode())
        if stderr:
            logger.debug(stderr.decode())

        cmd = [git, "rev-parse", "HEAD"]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            return stdout.decode().strip(), tempdir
        if stderr:
            return stderr.decode().strip(), tempdir

    finally:
        pass


# FIXME(cutwater): Remove try: .. finally: pass
async def sync_project(project_id, large_data_id, tempdir, db: AsyncSession):

    try:

        await find_rules(project_id, tempdir, db)
        await find_inventory(project_id, tempdir, db)
        await find_extra_vars(project_id, tempdir, db)
        await find_playbook(project_id, tempdir, db)
        await tar_project(project_id, large_data_id, tempdir, db)

    finally:
        pass


def is_rules_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if "rules" not in entry:
                    return False
    except Exception:
        logger.exception(filename)
        return False

    return True


def yield_files(project_dir):

    for root, _dirs, files in os.walk(project_dir):
        if ".git" in root:
            continue
        for f in files:
            yield root, f


async def insert_rulebook_related_data(
    rulebook_id: int, rulebook_data: dict, db: AsyncSession
):
    ruleset_values = [
        {"name": ruleset_data["name"], "rulebook_id": rulebook_id}
        for ruleset_data in rulebook_data
    ]
    query = (
        insert(models.rulesets)
        .returning(models.rulesets.c.id)
        .values(ruleset_values)
    )
    ruleset_ids = (await db.scalars(query)).all()

    rule_values = [
        {"name": rule["name"], "action": rule["action"], "ruleset_id": rsid}
        for rsid, rsdata in zip(ruleset_ids, rulebook_data)
        for rule in rsdata["rules"]
    ]
    query = insert(models.rules).values(rule_values)
    await db.execute(query)


async def find_rules(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if not is_rules_file(full_path):
            continue

        with open(full_path) as f:
            rulesets = f.read()

        query = insert(rulebooks).values(
            name=filename, rulesets=rulesets, project_id=project_id
        )
        (rulebook_id,) = (await db.execute(query)).inserted_primary_key
        # TODO(cutwater): Remove debugging print
        logger.debug(rulebook_id)

        rulebook_data = yaml.safe_load(rulesets)
        await insert_rulebook_related_data(rulebook_id, rulebook_data, db)


def is_inventory_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, dict):
                return False
            if "all" not in data:
                return False
    except Exception:
        logger.exception(filename)
        return False

    return True


async def find_inventory(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_inventory_file(full_path):
            with open(full_path) as f:
                inventory = f.read()

            query = insert(inventories).values(
                name=filename, inventory=inventory, project_id=project_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


def is_playbook_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if "tasks" in entry:
                    return True
                if "roles" in entry:
                    return True
    except Exception:
        logger.exception(filename)
        return False
    return False


def is_extra_vars_file(filename):
    if not filename.endswith(".yml"):
        return False
    return (
        not is_rules_file(filename)
        and not is_inventory_file(filename)
        and not is_playbook_file(filename)
    )


async def find_extra_vars(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_extra_vars_file(full_path):
            with open(full_path) as f:
                extra_var = f.read()

            query = insert(extra_vars).values(
                name=filename, extra_var=extra_var, project_id=project_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


async def find_playbook(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_playbook_file(full_path):
            with open(full_path) as f:
                playbook = f.read()

            query = insert(playbooks).values(
                name=filename, playbook=playbook, project_id=project_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


async def tar_project(
    project_id, large_data_id, project_dir, db: AsyncSession
):

    with tempfile.TemporaryDirectory() as tempdir:

        tarfile_name = os.path.join(tempdir, "project.tar.gz")

        cmd = [tar, "zcvf", tarfile_name, "."]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            logger.critical(stdout.decode())
        if stderr:
            logger.critical(stderr.decode())

        logger.critical(tarfile_name)

        async with PGLargeObject(db, oid=large_data_id, mode="w") as lobject:
            with open(tarfile_name, "rb") as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    await lobject.write(data)
            await db.commit()
