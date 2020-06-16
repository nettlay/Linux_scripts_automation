#!/bin/bash
pkill -KILL xfsettingsd
pkill -TERM xfconfd
currentUser=""
user=$(mclient --quiet get tmp/encryption/session/currentUser/user)
domain=$(mclient --quiet get tmp/encryption/session/currentUser/domain)
if [ -n "$user" -a -n "$domain" ]
then
	currentUser=$(getnet passwd "${domain}\\${user}" | cut -d: -f1)
else
	currentUser="user"
fi
sudo -u $currentUser DISPLAY=:0 /usr/bin/xfsettingsd
