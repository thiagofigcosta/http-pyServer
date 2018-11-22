#!/usr/bin/env python
# -*- coding: utf-8 -*-

def intToAlphabet(number):
	alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
	result = ''
	while number >= len(alphabet):
		div, mod = divmod(number, len(alphabet))
		result = alphabet[mod] + result
		number = int(div)
	result=alphabet[number] + result
	return result


def intToAlphabet2(number):
	alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
	result = ''
	while number >= len(alphabet):
		result = result +alphabet[len(alphabet)-1]
		number = number-len(alphabet)
	result=result+	alphabet[number]
	return result

def intToAlphabet3(number,maxsize):
	max=intToAlphabet2(maxsize);
	alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
	result = ''
	while number >= len(alphabet):
		result = result +alphabet[len(alphabet)-1]
		number = number-len(alphabet)
	result=result+alphabet[number]
	while len(result)<len(max):
		result="A"+result
	return result