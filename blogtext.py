#!/bin/python3
# vim: noet:ts=2:sts=2:sw=2

# SPDX-License-Identifier: MIT
# Copyright © 2024 David Llewellyn-Jones

from html.parser import HTMLParser
from html import escape
import re

class ValidateParser(HTMLParser):
	def __init__(self, text):
		super(ValidateParser, self).__init__()
		self.depth = 0
		self.stack = []
		self.lines = text.split('\n')

	def handle_starttag(self, tag, attrs):
		self.depth += 1
		self.stack.append(tag)

	def handle_endtag(self, tag):
		self.depth -= 1
		if (self.stack[-1:] != [tag]):
			pos = self.getpos()
			if len(self.stack) > 0:
				endtag = self.stack[-1:]
			else:
				endtag = "None"
			print('Error with tag "{}/{}" on line {}, character {}'.format(tag, endtag, pos[0], pos[1]))
			print('{}'.format(self.lines[pos[0] - 1]))
		self.stack = self.stack[:-1]

	def handle_startendtag(self, tag, attr):
		pass

	def handle_data(self, data):
		pass

class BlogParser(HTMLParser):
	def __init__(self):
		self.depth = 0
		self.stack = []
		self.text = ''
		self.pre = False
		self.tt = False
		self.chunk = ''
		self.tt_chunk = ''
		super(BlogParser, self).__init__()

	def split_line(self, line):
		result = []
		indent = False
		while len(line) > 0:
			maxlen = 76 if indent else 80
			prefix = '    ' if indent else ''
			if len(line) > maxlen:
				split = re.search(r'.*[ \t(:/]', line[:maxlen])
				if split:
					result.append(prefix + line[:split.end()])
					indent = True
					line = line[split.end():]
				else:
					result.append(prefix + line)
					line=''
			else:
				result.append(prefix + line)
				line=''
		if len(result) == 0:
			result = ['']
		return result

	def split_lines(self, text):
		lines = text.split('\n')
		text = ''
		for line in lines:
			split = self.split_line(line)
			if len(split) > 1:
				text += split[0] + '\n' + '\n'.join(split[1:]) + '\n'
			else:
				text += split[0] + '\n'
		text = text.strip('\n')
		return text

	def convert_literal(self, text):
		text = escape(text)
		return text

	def convert_pre(self, text):
		text = re.sub(r'/usr/src/debug/xulrunner-qt5-[a-z0-9\+\-\.\_]+/', '', text)
		text = re.sub(r'/home/abuild/rpmbuild/BUILD/xulrunner-qt5-[a-z0-9\+\-\.\_]+/', '', text)
		text = re.sub(r'/srv/mer/toings/SailfishOS-[0-9\.]+/opt/cross/[a-z0-9-]+/', '', text)
		text = re.sub(r'/home/flypig/Documents/Development/jolla/gecko-dev-esr91/gecko-dev/', '${PROJECT}/', text)
		text = self.split_lines(text)
		text = self.convert_literal(text)
		return '<pre>\n{}\n</pre>\n\n'.format(text)

	def convert_tt(self, text):
		text = self.convert_literal(text)
		return '<tt>{}</tt>'.format(text)

	def convert_text(self, text):
		text = text.strip('\n')
		paras = text.split('\n\n')
		text = ''
		for count in range(len(paras)):
			para = paras[count]
			if count < (len(paras) - 1):
				next = paras[count + 1]
			else:
				next = ''

			if para[:7] == '## Day ':
				text += '{}\n\n'.format(para)
			elif count == len(paras) - 1:
				text += '{}'.format(para)
			elif para[:25] == '<div class="float_centre"':
				text += '{}\n<br />\n\n'.format(para)
			elif para[:18] == '<div class="quote"':
				text += '{}\n<br />\n\n'.format(para)
			elif para[:3] == '<ol' or para[:3] == '<ul':
				text += '{}\n\n'.format(para)
			elif next[:3] == '<ol' or next[:3] == '<ul':
				text += '{}\n<br />\n\n'.format(para)
			else:
				text += '{}\n<br /><br />\n\n'.format(para)
		return text

	def handle_starttag(self, tag, attrs):
		self.depth += 1
		self.stack.append(tag)
		if tag == 'pre':
			self.pre = True
			if len(self.chunk.strip('\n')) > 0:
				self.text += self.convert_text(self.chunk)
				self.text += '\n\n'
			self.chunk = ''
		elif tag == 'tt' and not self.pre:
			self.tt = True
		else:
			self.chunk += self.get_starttag_text()

	def handle_endtag(self, tag):
		self.depth -= 1
		self.stack = self.stack[:-1]
		if tag == 'pre' and self.pre:
			self.pre = False
			self.text += self.convert_pre(self.chunk)
			self.chunk = ''
		elif tag == 'tt' and self.tt:
			self.tt = False
			self.chunk += self.convert_tt(self.tt_chunk)
			self.tt_chunk = ''
		else:
			self.chunk += '</{}>'.format(tag)

	def handle_startendtag(self, tag, attr):
			self.chunk += self.get_starttag_text()

	def handle_data(self, data):
		if self.tt:
			self.tt_chunk += data
		else:
			data = re.sub(r'—', '&mdash;', data)
			data = re.sub(r'"', '&quot;', data)
			self.chunk += data

	def finish(self):
		if len(self.chunk.strip('\n')) > 0:
			self.text += self.convert_text(self.chunk)
			self.text += '\n\n'
		return self.text

html = ''
with open('in.html') as fh:
	html = fh.read()

parser = BlogParser()
parser.feed(html)
text = parser.finish()
print(text)

validate = ValidateParser(text)
validate.feed(text)


