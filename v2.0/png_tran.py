# -*- coding: cp936 -*-
import networkx as nx
import matplotlib.pyplot as plt
import os
import seq_ex
import multiprocessing
import sys

# 通过最终网络图文件计算最终坐标
def cal_scale(final_file):
	x_max = 0
	y_max = 0
	n_x_max = -1
	n_y_max = -1
	G = nx.read_graphml(final_file)
	for node_id, attrs in G.nodes(data=True):
		# if x_max < attrs['x'] or y_max < attrs['y']:
		# 	print('+' + final_file)
		# if n_x_max > attrs['x'] or n_y_max > attrs['y']:
		# 	print('-' + final_file)
		x_max = max(x_max, attrs['x'])
		y_max = max(y_max, attrs['y'])
		n_x_max = min(n_x_max, attrs['x'])
		n_y_max = min(n_y_max, attrs['y'])
	return x_max, y_max, n_x_max, n_y_max

# 计算所有点的最大坐标
def cal_max(nodes, node_list):
	x_max = 0
	y_max = 0
	n_x_max = -1
	n_y_max = -1
	for node in nodes:
		x_max = max(x_max, node_list[node][0])
		y_max = max(y_max, node_list[node][1])
		n_x_max = min(n_x_max, node_list[node][0])
		n_y_max = min(n_y_max, node_list[node][1])
	return x_max, y_max, n_x_max, n_y_max

def main(file_name):
	x_max, y_max, n_x_max, n_y_max = cal_scale('ex/' + file_name)
	seq_dir = 'seq_image_2_hour/' + file_name[:-11]
	os.mkdir(seq_dir)
	node_coors = dict()
	node_reflect = dict()
	node_time = dict()
	node_list = []
	ori_G = nx.read_graphml('ex/' + file_name)
	print(u'[ 读取图：%s ] [ 节点数：%d ] [ 边数：%d ]' % (file_name, ori_G.number_of_nodes(), ori_G.number_of_edges()))
	for node_id, attrs in ori_G.nodes(data=True):
		node_coors[node_id] = (attrs['x'], attrs['y'])
		node_list.append((attrs['x'], attrs['y']))
		node_reflect[node_id] = len(node_reflect)
		node_time[attrs['m_timestamp']] = node_reflect[node_id]
	first_hour_nodes, node_seq = seq_ex.cut_series(node_time)
	x_max, y_max, n_x_max, n_y_max = cal_max(first_hour_nodes, node_list)
	# x_max, y_max, n_x_max, n_y_max = cal_scale('ex/' + file_name)
	for time, nodes in node_seq.items():
		G = nx.Graph()
		edges_list = []
		for node_id, attrs in ori_G.nodes(data=True):
			for to_node, _ in ori_G[node_id].items():
				if node_reflect[node_id] in nodes and node_reflect[to_node] in nodes:
					edges_list.append((node_reflect[node_id], node_reflect[to_node]))
		G.add_edges_from(edges_list)
		# 新建画布，重要
		plt.figure(0)
		nx.draw(G, node_list, with_labels=False, node_size=1, node_color='black', width=0.15, style='dotted')
		plt.xlim(n_x_max, x_max)
		plt.ylim(n_y_max, y_max)
		# plt.show()
		file_name = file_name.split('.')[0]
		# plt.show()
		plt.savefig(seq_dir + '/' + time + '.png')
		# 关闭图，重要
		plt.close(0)
		# exit(1)

def batch_process(files):
	for file in files:
		main(file)

if __name__ == '__main__':
	all_files = []
	for parent, dirnames, filenames in os.walk('ex'):
		for file in filenames:
			all_files.append(file)
	process_num = int(sys.argv[1])
	ave = int(len(all_files) / process_num) + 1
	for i in range(1, process_num + 1):
		files = all_files[ave * (i-1): ave * i]
		p = multiprocessing.Process(target=batch_process, args=(files,))
		p.start()