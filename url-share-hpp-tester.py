from bs4 import BeautifulSoup
from termcolor import colored
from urllib import request, parse
import argparse
import sys

g_domain = ""
g_param = {
	'u': 'https://fsec404.github.io'
}
urls_to_go_to = []

g_depth = 0
g_max_depth = 2

"""
	Encodes the user's parameters for pollution.
"""
def encode_param():
	global g_param
	g_param = parse.urlencode(g_param)


"""
	Converts a relative link to an absolute one and appends our paramter.
"""
def create_url(url):
	# Convert relative link to absolute; no need to check if it is relative or not as urljoin handles it
	url = parse.urljoin(g_domain, url)
	return (url+ "?&" + g_param)


"""
	Sets the HTTP headers.
"""
def set_headers():
	opener = request.build_opener()
	opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
	request.install_opener(opener)


"""
	Checks if the url is a facebook share link, using the sharer mecahnism, with our parameter polluting it.
"""
def is_polluted_fb_url(url):
	fb_str = "https://www.facebook.com/sharer/sharer.php"
	fs = "&u=https://fsec404.github.io"
	fs_encoded = "&u=https%3A%2F%2Ffsec404.github.io"

	if (fb_str in str(url) and
		(fs in str(url) or fs_encoded in str(url))):
		return True
	else:
		return False

"""
	Checks if the url can be polluted by our paramter.
"""
def pollution_tester(url):
	global urls_to_go_to, g_depth

	if (g_depth > g_max_depth):
		return

	url = create_url(url)
	print(colored("[*] Trying: "+url, "red"))

	x = request.urlopen(url)
	soup = BeautifulSoup(x.read(), 'html.parser')

	urls_to_go_to.append([])
	for tag in soup.find_all('a'):
		urls_to_go_to[g_depth].append(tag.get('href'))

	#print(urls_to_go_to[g_depth])
	for url in urls_to_go_to[g_depth]:
		if (is_polluted_fb_url(url)):
			print(colored("[*] Possible pollution: "+url, "green"))
			sys.exit(0)


	if (g_depth < g_max_depth):
		for url in urls_to_go_to[g_depth]:
			g_depth += 1
			pollution_tester(url)
			g_depth -= 1


def main():
	global g_domain

	parser = argparse.ArgumentParser()
	parser.add_argument("-d", help="Specify the target domain")
	parser.add_argument("-r", help="Override default recursion depth.")
	args = parser.parse_args()

	g_domain = args.d

	if (g_domain == None):
		sys.exit("[#] Please specify a target domain")
	if (args.r != None):
		g_max_depth = args.r
		print(colored("[*] Changing recursion depth to: "+g_max_depth, "green"))

	print(colored("[*] Domain: "+g_domain,"green"))

	set_headers()
	encode_param()
	pollution_tester(g_domain)


if __name__ == "__main__":
	main()

