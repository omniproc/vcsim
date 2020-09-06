FROM golang:1.15.1 as builder
LABEL name="vCenter Appliance Simulator"
LABEL description="A VMware vCenter API mock server based on govmomi"
LABEL url="https://github.com/vmware/govmomi/vcsim"
RUN go get -u github.com/vmware/govmomi/vcsim
RUN go get -u github.com/vmware/govmomi/govc
FROM photon:3.0
COPY --from=builder /go/bin/govc .
COPY --from=builder /go/bin/vcsim .
ADD /ssl/untrusted_cert.pem ./untrusted_cert.pem
ADD /ssl/untrusted_key.pem ./untrusted_key.pem
ENTRYPOINT ["./vcsim"]
CMD ["-httptest.serve", "0.0.0.0:8989", "-tls", "-tlscert", "/untrusted_cert.pem", "-tlskey", "/untrusted_key.pem"]
