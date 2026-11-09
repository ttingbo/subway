import streamlit as st
import pandas as pd
import folium
import streamlit.components.v1 as components
from pathlib import Path


class Dijkstra:
    def __init__(self,nodes):
        self.g = {}
        self.dist = {}
        for node in nodes:
            self.g[node] = {}
            self.dist[node] = [float("inf"), "none"]

    def setEdge(self, a, b, w, bidirection=True):
        self.g[a][b] = w
        if bidirection == True: self.g[b][a] = w

    def getPath(self, start, end):
        nodes = set(self.g)
        dictfilt = lambda x, y: dict([(i, x[i]) for i in x if i in set(y)])
        visits = set()
        curNode = start
        self.dist[curNode][0] = 0
        while True:
            visits.add(curNode)
            nodes.remove(curNode)
            neighbors = self.g[curNode]

            for node in neighbors:
                if min(self.dist[node][0], self.dist[curNode][0] + self.g[curNode][node]) < self.dist[node][0]:
                    self.dist[node][0] = min(self.dist[node][0], self.dist[curNode][0] + self.g[curNode][node])
                    self.dist[node][1] = curNode

            if len(nodes) > 0:
                curNode = min(dictfilt(self.dist, nodes), key=dictfilt(self.dist, nodes).get)
            else:
                break

        path = [end]
        dist = []

        while end != start:
            path.append(self.dist[end][1])
            dist.append(self.dist[end][0])
            end = self.dist[end][1]

        return path[::-1], dist[::-1]


folder = Path(__file__).parent
data = pd.read_csv(folder / 'subway.csv', header=None)
location = pd.read_csv(folder / 'subwayLocation.csv', header=None)
graph = data.values.tolist()

nodes = set()
for node in graph:
    nodes.add(node[0])
    nodes.add(node[1])

st.title('지하철 최단 경로')
st.caption('제공된 subway.csv의 역간 시간을 기준으로 계산합니다.')
stations = sorted(nodes)
start = st.selectbox('출발역', stations, index=stations.index('서울역(1)'))
end = st.selectbox('도착역', stations, index=stations.index('강남(2)'))

if st.button('최단 경로 찾기'):
    d = Dijkstra(nodes)
    for node in graph:
        d.setEdge(node[0], node[1], node[2])

    path, dist = d.getPath(start, end)
    st.subheader('검색 결과')
    st.write(' → '.join(path))
    st.write('총 소요 시간:', d.dist[end][0], '분')

    points = []
    m = folium.Map(location=[37.55, 126.98], zoom_start=12)
    for station in path:
        name = station.rsplit('(', 1)[0]
        row = location[location[0] == name].iloc[0]
        point = [float(row[1]), float(row[2])]
        points.append(point)
        folium.Marker(point, tooltip=station).add_to(m)

    if len(points) > 1:
        folium.PolyLine(points, color='red', weight=5).add_to(m)
        m.fit_bounds(points)
    else:
        m.location = points[0]

    components.html(m.get_root().render(), height=550)
