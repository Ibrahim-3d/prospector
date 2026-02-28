from scrapling import Selector
html = b'<html><body><div class="job"><h2 class="title">T</h2></div></body></html>'
page = Selector(html)
jobs = page.css('.job')
print("Page methods:", [m for m in dir(page) if 'css' in m])
print("Jobs list type:", type(jobs))
print("Job element type:", type(jobs[0]))
print("Job element methods:", [m for m in dir(jobs[0])])
