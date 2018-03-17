import networkx as nx

# 2016-06-01T20:34:27.000+0800
def cut_series(node_time):
	node_time = sorted(node_time.items(), key=lambda item: item[0])
	node_seq = {}
	first_hour_all_node = []
	for j in range(1, 5):
		node_seq[str(j * 1800)] = []
		for i in range(len(node_time)):
			if int(node_time[0][0]) <= int(node_time[i][0]) <= int(node_time[0][0]) + j * 1800:
				node_seq[str(j*1800)].append(node_time[i][1])
				if node_time[i][1] not in first_hour_all_node:
					first_hour_all_node.append(node_time[i][1])
				# node_seq.append(node_time[i])
	return first_hour_all_node, node_seq
	# print(node_seq)
# if __name__ == '__main__':
# 	read_time('9543_ex.graphml')