# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2018 Robert Ruf
# SPDX-License-Identifier: MIT
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ssl
import urllib
import socket
import logging
import argparse
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl  # pylint: disable=no-name-in-module


__author__ = "Robert Ruf"
__copyright__ = "Copyright 2018, Robert Ruf"
__license__ = "MIT"


# __CONFIGURATION________________________________________________________________________________________________________
# _______________________________________________________________________________________________________________________
_APPLICATION = "vcsimtest"
_DESCRIPTION = "Test basic VCSIM functionality with PyVmomi."

logger = logging.getLogger()
enable_debug = False
disable_ssl = False

# VCSIM mocking server configuration data
hostname = "127.0.0.1"
hostport = 8989
ca_chain = """-----BEGIN CERTIFICATE-----
MIIDGjCCAgKgAwIBAgIBNDANBgkqhkiG9w0BAQsFADAvMQswCQYDVQQGEwJERTEg
MB4GA1UEAwwXVkNTSU1fVU5UUlVTVEVEX1JPT1RfQ0EwIBcNMTgxMjExMDAwMDAw
WhgPMjExODEyMTAyMzU5NTlaMC8xCzAJBgNVBAYTAkRFMSAwHgYDVQQDDBdWQ1NJ
TV9VTlRSVVNURURfUk9PVF9DQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBALb3YObGiRBlW2j20TMvZ2pZ8IyIxIgUZhK5WqwdFbIH91W9fU6g4ahARufA
IRyW5hIsX4HVsgaqM4+NkaFi0/rR1dI1oBHiRH8w2g2LXV2pIospEJP6M0gpN7bL
aVgzXboYBwG9hEDlOXjQlh8VBsN1HqE2X94Cf0cIpoW7Wu2TR07WhGt94rQYEsIF
7fO5YOzf/B81+5/trbXmapJMqYq/u3wxhRs9M/IQw4l6vORQSi31P2lxrVbJf3+k
iOqllZ53UOKnU7Mk2AW2n5SwRYnw7SClLFNV9Kuo4xgYRi2pY1PJf9TisY1QShq8
CSXu1DfTzWt/y6IarmPdVGgd3ZUCAwEAAaM/MD0wDwYDVR0TAQH/BAUwAwEB/zAd
BgNVHQ4EFgQUtqn6gZrHumWkd2UutkOiEB6y/JEwCwYDVR0PBAQDAgEGMA0GCSqG
SIb3DQEBCwUAA4IBAQB6d3NnTOkvqh7IPugbQivXz4r9hV46wqQnbw0XU6C1DWeJ
TGsS035VCg7pU2QfkhvEGO5s6yb+6HBBT7NgqysJ897NNjU3RzEoOiQaEJQaChMf
DxJZzllp/YGzb8fNn4tE240ZCpJKCZfQlnvb+Jc0GsQnvRD8POl/NpzSmUH5gWxQ
Sadbtaa4kTzl5FsizhB11uyOwoucY6r3GzeQ1Gccw2P3NK6QBx8veN/k78MDNoWJ
p++eu5uhPEgI0d2R7bZW4N3P+1AcI4CP6Qm2V7X735RGxAcurI50qrbsJrQIAeiD
IBVkETbP+DNB9/1/IhMeSMwuvQk08tG2BZzBpmNs
-----END CERTIFICATE-----
"""

# __EXECUTION____________________________________________________________________________________________________________
# _______________________________________________________________________________________________________________________


try:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.prog = _APPLICATION
    parser.add_argument("-s", action="store", dest="hostname", default="127.0.0.1", help="server hostname of the VCSIM.")
    parser.add_argument("-p", action="store", dest="hostport", default=8989, help="server SSL port of the VCSIM.")
    parser.add_argument("--nossl", action="store_true", dest="disable_ssl", default=False, help="disable SSL validation.")
    parser.add_argument("--debug", action="store_true", dest="enable_debug", default=False, help="enable debug logging.")
except Exception as ex:
    raise SystemExit(f"Error: argsparse setup failed. Reason: {ex}. Exiting.")


def configure_basic_logger(level: int=logging.WARNING) -> logging.Logger:
    logger.handlers = []
    if(not level):
        level = logging.WARNING
    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)
    logger.setLevel(level)
    return logger


def get_ssl_context(ca_cert: str=None, validate: bool=True) -> ssl.SSLContext:
    ssl_context = None
    try:
        if(not validate):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_context.verify_flags = ssl.VERIFY_DEFAULT
            logger.warning("Using untrusted SSL connection.")
        elif(ca_cert is not None):
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cadata=ca_cert)
            ssl_context.verify_flags = ssl.VERIFY_DEFAULT
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.check_hostname = True
            ssl_context.options |= ssl.OP_NO_TLSv1
            ssl_context.options |= ssl.OP_NO_TLSv1_1
            logger.debug("Using provided CA certificate(s)")
        else:
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.verify_flags = ssl.VERIFY_DEFAULT
            ssl_context.options |= ssl.OP_NO_TLSv1
            ssl_context.options |= ssl.OP_NO_TLSv1_1
            logger.warning("Using system default trusted root CA stores.")
    except Exception:
        raise Exception("Error: failed to create SSL context.")
    return ssl_context


def vcsim_ping(hostname: str, hostport: int, ssl_context: ssl.SSLContext, connection_timeout: int = 5) -> None:
    try:
        vcsim_url = urllib.parse.urlparse(f"https://{hostname}:{str(hostport)}")
        logger.info(f"Testing connectivity with VCSIM '{hostname}:{str(hostport)}'...")
        with urllib.request.urlopen(vcsim_url.geturl(), context=ssl_context, timeout=connection_timeout) as response:
            logger.info(f"Connected to VCSIM '{hostname}:{str(hostport)}' without any issues ({str(response.status)}).")
    except urllib.error.HTTPError as ex:
        # This is a connection test. Only fail if the server is unreachable (x>500).
        if(ex.code >= 500):
            raise SystemExit(f"HTTPError '{str(ex.code)}' was raised  while testing connectivity with VCSIM '{hostname}:{str(hostport)}'.")
        else:
            logger.warning(f"Connected to VCSIM '{hostname}:{str(hostport)}' with issues ({str(ex.code)}), but that's fine!")
    except urllib.error.URLError as ex:
        raise SystemExit(f"URLError was raised while testing connectivity with VCSIM '{hostname}:{str(hostport)}'. Reason: {ex.reason}.")
    except (TimeoutError, socket.timeout):
        raise SystemExit(f"Request to VCSIM '{hostname}:{str(hostport)}' timed out. Host unreachable.")
    except (Exception, OSError):
        raise SystemExit(f"Unable to connect to VCSIM '{hostname}:{str(hostport)}'.")


def vcsim_list(hostname: str, hostport: int, ssl_context: ssl.SSLContext, username="user", password="pass") -> None:
    logger.info("Executing vCenter operations...")
    try:
        session = SmartConnect(host=hostname, port=hostport, sslContext=ssl_context, user=username, pwd=password)
        dc = session.content.rootFolder.childEntity[0]
        vms = dc.vmFolder.childEntity
        logger.info("Listing VMs...")
        for vm in vms:
            logger.info(f"{vm.name}")
    except Exception as ex:
        raise SystemExit(f"Failed performing vCenter operation: {ex}")


def vcsim_test(hostname: str, hostport: int, ssl_context: ssl.SSLContext, username="user", password="pass", connection_timeout: int = 5) -> None:
    vcsim_ping(hostname=hostname, hostport=hostport, ssl_context=ssl_context, connection_timeout=connection_timeout)
    vcsim_list(hostname=hostname, hostport=hostport, ssl_context=ssl_context, username=username, password=password)


def main():
    # Declare variables to hold the required arguments passed to argsparse
    try:
        # Get argument parameters
        args = parser.parse_args()
        hostname = args.hostname
        hostport = args.hostport
        disable_ssl = args.disable_ssl
        enable_debug = args.enable_debug
    except Exception:
        # Exit and log to StdErr
        raise SystemExit("Error: unable to parse require input arguments. Exiting.")

    if(enable_debug):
        configure_basic_logger(logging.DEBUG)
    else:
        configure_basic_logger(logging.INFO)

    logger.info("Starting PyVmomi tests for VCSIM...")

    ssl_context = None
    if(disable_ssl):
        ssl_context = get_ssl_context(ca_cert=ca_chain, validate=False)
    else:
        ssl_context = get_ssl_context(ca_cert=ca_chain)

    vcsim_test(hostname=hostname, hostport=hostport, ssl_context=ssl_context)

    logger.info("Successed PyVmomi tests for VCSIM.")


if __name__ == "__main__":
    main()
