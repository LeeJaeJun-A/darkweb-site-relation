import requests, time, subprocess, threading 
from bs4 import BeautifulSoup
import pydot
import sys
import io

# Python의 기본 인코딩을 UTF-8로 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

proxies = {
    "http" : "socks5h://127.0.0.1:9150",
    "https" : "socks5h://127.0.0.1:9150"
}

def safe_text(text):
    return text.replace('\u2013', '-')

def make_relation(urls, depth, graph = None):
    if depth == 0:
        return graph

    if graph is None:
        graph = pydot.Dot("relation", graph_type = "digraph", rankdir="LR")

    for url in urls:
        print(url)
        if not any(node.get_name() == url for node in graph.get_node_list()):
            graph.add_node(pydot.Node(url))

        try:
            response = requests.get(url, proxies=proxies, allow_redirects=True)
            print(response.status_code)
            soup = BeautifulSoup(response.content, "html.parser")
            response.close()
        except:
            continue

        links = []

        for a in soup.find_all("a"):
            try:
                href = a['href']
                if href.startswith('#') or href.startswith('javascript:') or len(href) == 0:
                    continue
                if href.startswith('//'):
                    href = "https:" + href
                elif href.startswith('/'):
                    href = url.rstrip('/') + href
                if href.startswith('http') and href not in links:
                    links.append(href)
                    if not any(node.get_name() == href for node in graph.get_node_list()):
                        graph.add_node(pydot.Node(href))
                    graph.add_edge(pydot.Edge(url, href))

            except Exception as e:
                print(f"Error: {e}")
                continue
        
        time.sleep(1)
        
        if links:
            make_relation(links, depth - 1, graph)
    return graph

base_url = ["http://ly75dbzi2yrzkugzfrgn4zbp2unpjpyth3qopbfthscunlpdfypi3lqd.onion"]
depth = 1
graph = make_relation(base_url, depth)
graph.write_png("relation.png")
