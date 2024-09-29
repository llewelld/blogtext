#!/bin/bash
# vim: noet:ts=2:sts=2:sw=2

# SPDX-License-Identifier: MIT
# Copyright © 2024 David Llewellyn-Jones

from datetime import datetime, timedelta

dates = []

with open("diary-dates.txt", "r") as fh:
	for line in fh:
		# Strip comments
		line = line.strip("\n")
		pos = line.find("#")
		if pos >= 0:
			line = line[:pos]
		if len(line) > 0:
			day = datetime.strptime(line, "%d %b %Y")
			day = day + timedelta(days=1)
			dates.append(day)

week_days = 0
weekend_days = 0

for date in dates:
	weekday = date.weekday()
	if weekday < 5:
		week_days += 1
	else:
		weekend_days += 1

print("Week days: {}".format(week_days))
print("Weekend days: {}".format(weekend_days))

