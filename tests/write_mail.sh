#!/bin/bash

MAIL_FILE="tests/mail.txt"

cat $(echo $1 | sed 's|^file://||') > "$MAIL_FILE"
