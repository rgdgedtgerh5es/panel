FROM ghcr.io/mhsanaei/3x-ui:v2.9.0

COPY web /opt/vpnstan/web
COPY scripts/start.sh /start-vpnstan.sh
RUN chmod +x /start-vpnstan.sh

ENV VPNSTAN_WEB=/opt/vpnstan/web
ENV VPNSTAN_PORT=3000

EXPOSE 3000
VOLUME ["/etc/x-ui"]

ENTRYPOINT ["/start-vpnstan.sh"]
