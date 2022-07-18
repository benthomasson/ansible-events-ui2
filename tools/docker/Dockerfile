# Build UI
FROM docker.io/node:16-alpine AS ui-builder
WORKDIR /app
COPY . $WORKDIR
RUN cd ui && npm install && npm run build


# Build app
FROM registry.access.redhat.com/ubi9/python-39
ARG USER_ID=${USER_ID:-1001}
ARG DEVEL_AE_LIBRARY=0
USER 0

WORKDIR $HOME
COPY . $WORKDIR
COPY --from=ui-builder /app/ui/dist/ ./ui/dist
RUN mkdir sqlite

RUN chown -R $USER_ID ./
USER $USER_ID

RUN pip install '.[sqlite]'

RUN bash -c "if [ $DEVEL_AE_LIBRARY -ne 0 ]; then \
    pip uninstall ansible-events && \
    pip install git+https://github.com/benthomasson/ansible-events.git; fi"

CMD ["ansible-events-ui"]