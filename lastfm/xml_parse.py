from lxml import etree

def parse(string):
	# Returns a tree of parsed XML data
	parser = etree.XMLParser(recover=True)
	return etree.fromstring(string)
	