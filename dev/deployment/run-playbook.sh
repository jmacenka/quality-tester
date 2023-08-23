#!/bin/sh
# Script to run the ansible-playbook inlcuding the credentaisl fiel and inventory
# Created by Jan Macenka @ 23 Aug 2023

ansible-playbook -i inventory.ini playbook-setup-rpi-with-quality-tester.yml --ask-vault-pass