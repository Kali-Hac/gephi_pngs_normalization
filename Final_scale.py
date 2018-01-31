#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☆*°☆*°(∩^o^)~━━  2018/1/28 15:31        
      (ˉ▽￣～) ~~ 一捆好葱 (*˙︶˙*)☆*°
      Fuction： 计算最后一个时刻的网络图缩放至1024*1024的比例系数 √ ━━━━━☆*°☆*°
"""
import networkx as nx

def cal_scale(file_name):
	_max = 0
	G = nx.read_graphml(file_name)
	for node_id, attrs in G.nodes(data=True):
		_max = max(_max, abs(attrs['x']))
		_max = max(_max, abs(attrs['y']))
	print(u'[ 最终网络图缩小比例：%f ]' % ((_max * 2 + 1.0) / 1024))
	return (_max * 2 + 1.0)/1024

def val_scale_trans(x, y, scale):
	# 转换至1024*1024的像素坐标，第一个像素点在左顶上角为(0, 0)
	x = float(x)/scale
	y = float(y)/scale
	x += 512
	y -= 512
	if y < 0:
		y = -y
	# 直接精确到个位
	x = round(x)
	y = round(y)
	assert x <= 1024
	assert y <= 1024
	x = min(round(x), 1023)
	y = min(round(y), 1023)
	return x, y

def Get_scale(file_name):
	scale = cal_scale(file_name)
	G = nx.read_graphml(file_name)
	for node_id, attrs in G.nodes(data=True):
		val_scale_trans(attrs['x'], attrs['y'], scale)
	return scale

