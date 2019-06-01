#!/usr/bin/env python2.7
#
# Start task for CentOS 7.3 render nodes
#
# Sets AZ_BATCH_XXX system wide environment variables
# Installs xinetd and any qube-* rpms
# Configures /etc/qb.conf
#

import os
import argparse


def set_system_wide_env():
    account_url = os.environ["AZ_BATCH_ACCOUNT_URL"]
    token = os.environ["AZ_BATCH_SOFTWARE_ENTITLEMENT_TOKEN"]

    account_url_line = "export AZ_BATCH_ACCOUNT_URL=%s\n"%account_url
    token_line = "export AZ_BATCH_SOFTWARE_ENTITLEMENT_TOKEN=%s\n"%token
    flexlm_line = "export FLEXLM_TIMEOUT=10000000\n"

    with open("/etc/profile", "a") as profile_file:
        profile_file.write("\n\n# Azure environment variables\n")
        profile_file.write(account_url_line)
        profile_file.write(token_line)
        profile_file.write(flexlm_line)


def configure_qbconf(supervisor_ip, worker_cluster):
    with open("/etc/qb.conf", "w") as qbconf_file:
        qbconf_file.write("qb_supervisor = %s\n"%supervisor_ip)
        qbconf_file.write("worker_cluster = %s\n"%worker_cluster)
        qbconf_file.write("qb_domain = qube\n")


def install_qube():
    cmd_line = "yum -y install xinetd; rpm -i ./qube-*.rpm"
    status = os.system(cmd_line)

    return status == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--supervisor-ip',
                        help="The local IP address of the Qube! supervisor",
                        required=True)
    parser.add_argument('-c', '--worker-cluster',
                        help="The Qube! cluster name to assign to the worker",
                        required=True)
    parser.add_argument('-n', '--no-install',action='store_true', help="Do not install Qube!")
    args = parser.parse_args()

    try:
        set_system_wide_env()
    except Exception, e:
        print "WARNING: Could not set system wide environment variables"
        print "\t%s"%str(e)

    if not args.no_install:
        if not install_qube():
            print "WARNING: Could not install Qube!"

    try:
        configure_qbconf(args.supervisor_ip, args.worker_cluster)
    except IOError:
        print "WARNING: Could not configure Qube!"

