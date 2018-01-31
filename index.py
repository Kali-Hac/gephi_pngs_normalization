#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☆*°☆*°(∩^o^)~━━  2018/1/26 20:59        
      (ˉ▽￣～) ~~ 一捆好葱 (*˙︶˙*)☆*°
      Fuction：提取gexf中每个点的坐标 √ ━━━━━☆*°☆*°
"""

from PIL import Image
import networkx as nx
import Final_scale
import os
import sys
import math

# 坐标按比例转换至最终的坐标系
def scale_trans(x, y, scale):
	# 转换至1024*1024的像素坐标，第一个像素点在左顶上角为(0, 0)
	x = float(x)/scale
	y = float(y)/scale
	x += 512
	y -= 512
	if y < 0:
		y = -y
	# 直接精确到个位
	assert x <= 1024
	assert y <= 1024
	x = int(min(round(x), 1023))
	y = int(min(round(y), 1023))
	return x, y

# 将在1024*1024的画布上画节点的位置上(2*2像素点,原坐标作为第一个像素点起点)
def draw_node_p(img, x, y):
	img.putpixel((x, y), (0, 0, 0))
	img.putpixel((min(x+1, 1023), y), (0, 0, 0))
	img.putpixel((x, min(y+1, 1023)), (0, 0, 0))
	img.putpixel((min(x+1, 1023), min(y+1, 1023)), (0, 0, 0))
	return img

# 连接两个节点的边，采用阶梯(1像素点)-水平线-阶梯的方法
def draw_edge(img, node_1, node_2):
	if node_1[0] == node_2[0]:
		for i in range(min(node_1[1], node_2[1]), max(node_1[1], node_2[1])):
			img.putpixel((node_1[0], i), (0, 0, 0))
	else:
		if node_1[0] > node_2[0]:
			x_t, y_t = node_1[0], node_1[1]
			node_1[0], node_1[1] = node_2[0], node_2[1]
			node_2[0], node_2[1] = x_t, y_t
		if node_1[1] == node_2[1]:
			for i in range(node_1[0], node_2[0]):
				img.putpixel((i, node_1[1]), (0, 0, 0))
		else:
			center_line = int((node_1[1] + node_2[1]) / 2)
			if node_1[1] > node_2[1]:
				front = node_1[1] - center_line
				end = center_line - node_2[1]
				front_p = node_1[0] + front
				end_p = node_2[0] - end
				for i in range(front):
					img.putpixel((min(node_1[0]+i, 1023), node_1[1]-i), (0, 0, 0))
				if front_p <= end_p:
					for i in range(front_p, min(end_p + 1, 1023)):
						img.putpixel((i, center_line), (0, 0, 0))
				else:
					for i in range(end_p, min(front_p + 1, 1023)):
						img.putpixel((i, center_line), (0, 0, 0))
				for i in range(end):
					img.putpixel((node_2[0] - i, min(node_2[1] + i, 1023)), (0, 0, 0))
			else:
				front = center_line - node_1[1]
				end = node_2[1] - center_line
				front_p = node_1[0] + front
				end_p = node_2[0] - end
				for i in range(front):
					img.putpixel((min(node_1[0] + i, 1023), min(node_1[1] + i, 1023)), (0, 0, 0))
				if front_p <= end_p:
					for i in range(front_p, min(end_p + 1, 1023)):
						img.putpixel((i, center_line), (0, 0, 0))
				else:
					for i in range(end_p, min(front_p + 1,1023)):
						img.putpixel((i, center_line), (0, 0, 0))
				for i in range(end):
					img.putpixel((node_2[0] - i, node_2[1] - i), (0, 0, 0))
	return img

# 连接两个节点的边，采用block_num * block_size  = max(width, height), block_num = min(height,width)
# 简而言之就是取两个节点构成的矩形的最长对角线方向，像素延伸取平均，最后一行/列随机应变(x或y坐标相等时亦另外处理)
def draw_edge_a(img, node_1, node_2):
	if node_1[0] == node_2[0]:
		for i in range(min(node_1[1], node_2[1]), max(node_1[1], node_2[1])):
			img.putpixel((node_1[0], i), (0, 0, 0))
	else:
		if node_1[0] > node_2[0]:
			x_t, y_t = node_1[0], node_1[1]
			node_1[0], node_1[1] = node_2[0], node_2[1]
			node_2[0], node_2[1] = x_t, y_t
		if node_1[1] == node_2[1]:
			for i in range(node_1[0], node_2[0]):
				img.putpixel((i, node_1[1]), (0, 0, 0))
		else:
			height = max(abs(node_1[1] - node_2[1]) - 2, 1)
			width = max(node_2[0] - node_1[0] - 2, 1)
			if width >= height:
				# block_num * block_size  = width, block_num = height
				block_size = int(math.floor(float(width / height)))
				if node_1[1] < node_2[1]:
					cur_x = node_1[0] + 2
					cur_y = node_1[1] + 2
					for i in range(0, height - 1):
						for j in range(0, block_size):
							img.putpixel((cur_x + j, cur_y + i), (0, 0, 0))
						cur_x += block_size
					for i in range(cur_x, node_2[0]):
						img.putpixel((i, cur_y + height - 1), (0, 0, 0))
				else:
					cur_x = node_1[0] + 2
					cur_y = node_1[1] - 1
					for i in range(0, height - 1):
						for j in range(0, block_size):
							img.putpixel((cur_x + j, cur_y - i), (0, 0, 0))
						cur_x += block_size
					for i in range(cur_x, node_2[0]):
						img.putpixel((i, cur_y - height + 1), (0, 0, 0))
			else:
				block_size = int(math.floor(float(height / width)))
				if node_1[1] < node_2[1]:
					cur_x = node_1[0] + 2
					cur_y = node_1[1] + 2
					for i in range(0, width - 1):
						for j in range(0, block_size):
							img.putpixel((cur_x + i, cur_y + j), (0, 0, 0))
						cur_y += block_size
					for i in range(cur_y, node_2[1] - 1):
						img.putpixel((cur_x + width - 1, i), (0, 0, 0))
				else:
					cur_x = node_1[0] + 2
					cur_y = node_1[1] - 1
					for i in range(0, width - 1):
						for j in range(0, block_size):
							img.putpixel((cur_x + i, cur_y - j), (0, 0, 0))
						cur_y -= block_size
					for i in range(node_2[1] + 2, cur_y + 1):
						img.putpixel((cur_x + width - 1, i), (0, 0, 0))
	return img

# 通过读取graphml文件来获取有向边和节点x,y位置，并启动1024*1024画布
	#PS： gml读取速度是graphml的1/6，而且节点输出值是标签(bug), 原库gexf读取存在bug不予采用
def extraction_re(file_name, final_scale):
	# 这个函数读取不了gexf(bug)
	# print(nx.read_gexf)
	node_coors = {}
	img = Image.new('RGB', (1024, 1024), (255, 255, 255))
	G = nx.read_graphml(file_name)
	print(u'[ 读取图：%s ] [ 节点数：%d ] [ 边数：%d ]' % (file_name, G.number_of_nodes(), G.number_of_edges()))
	# 在像素图上画每个节点，覆盖2*2像素块(以第一个点为原节点位置向左向下扩展)
	for node_id, attrs in G.nodes(data=True):
		x, y = scale_trans(attrs['x'], attrs['y'], final_scale)
		node_coors[node_id] = (x, y)
		img = draw_node_p(img, x, y)
	for node_id, attrs in G.nodes(data=True):
		for to_node, _ in G[node_id].items():
			# print(node_id, to_node)
			img = draw_edge_a(img, list(node_coors[node_id]), list(node_coors[to_node]))
	# img.show()
	return img
			# print(node_id, to_node)
		# print(node_id, (attrs['x'], attrs['y']))
	# for (u, v) in G.edges():
	#
	# 	print((u, v))

	# edges_iter只能读取无向图
	# for index in G.edges_iter(data=True):
	# 	print(index)

	# gml读取速度是graphml的1/6，而且节点输出值是标签(bug)
	# start = datetime.datetime.now()
	# G = nx.read_gml('a.gml')
	# print(G.nodes)
	# end = datetime.datetime.now()
	# print(end-start)

	# for index in G.edges(data=True):
	# 	print(index)
	# print(G.number_of_nodes())

if  __name__ == '__main__':
	# rootdir = "./ex"  # 指明被遍历的文件夹

	# result = extraction_re('tt.graphml', 10)
	# result.show()

	# 程序主入口，需要传入两个命令行参数，第一个为处理的图文件(graphml)所在的文件夹，第二个为最终的图文件(graphml)名字(寻找当前路径，因此需要放在当前目录)
	scale = Final_scale.Get_scale(sys.argv[2])
	for parent, dirnames, filenames in os.walk(sys.argv[1]):
		for file in filenames:
			result = extraction_re(sys.argv[1] + '/' + file, scale)
			result.save('./scale_pngs/' + file.split('.')[0] + '.png')
	print(u'[ 完成1024*1024规格化输出，保存至scale_pngs文件夹 ]')