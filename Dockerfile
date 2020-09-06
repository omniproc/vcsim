FROM golang:1.15.1 as builder
LABEL name="vCenter Appliance Simulator"
LABEL description="A VMware vCenter API mock server based on govmomi"
LABEL url="https://github.com/vmware/govmomi/vcsim"
RUN go get -u github.com/vmware/govmomi/vcsim
RUN go get -u github.com/vmware/govmomi/govc
FROM photon:3.0
COPY --from=builder /go/bin/govc .
COPY --from=builder /go/bin/vcsim .
ENTRYPOINT ["./vcsim"]
CMD ["-tls=0","-l=0.0.0.0:8989"]
