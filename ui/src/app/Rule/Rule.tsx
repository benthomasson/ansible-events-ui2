import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';

import Ansi from "ansi-to-react";
import {
  Card,
  CardBody as PFCardBody,
  CardTitle,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import styled from 'styled-components';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://localhost:8000/rulesetbook/';

const RuleSet: React.FunctionComponent = () => {

  const [ruleset, setRuleSet] = useState([]);

  let { id } = useParams();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleSet(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Rule Set {ruleset.name}</Title>
  </PageSection>
    <CodeBlock>
      <CodeBlockCode id="code-content">{ruleset.rules}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { RuleSet };
