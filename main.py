import os

from slacker import Slacker
slack = Slacker(os.environ['SLACK_API_KEY'])
bot_name = 'lokibot'
broadcast_channel = '#ssu-notices'

def create_link_message(semi_title, title, link):
	return {
		"color": "#36a64f",
		"author_name": semi_title,
		"title": title,
		"title_link": link
	}


from db import db_session_maker, UniversityNoticeModel


from celery import Celery
from datetime import datetime, timedelta


# celery for asynchronous jobs and periodic tasks
CELERY_BROKER_URL='redis://localhost:6379',
CELERY_RESULT_BACKEND='redis://localhost:6379'


celery_app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
celery_app.conf.update({
	'CELERY_ACCEPT_CONTENT': ['pickle', 'json', 'msgpack', 'yaml'],
	'CELERYBEAT_SCHEDULE': {
		'crawling-university-notices': {
			'task': 'task1',
			'schedule': timedelta(minutes=5)
		}
	},
	'CELERY_TIMEZONE': 'UTC'
})


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

@celery_app.task(name='task1')
def celery_task1():
	session = db_session_maker()

	lines = []
	board_link_format = 'http://m.ssu.ac.kr/html/themes/m/html/notice_univ_list.jsp?curPage={}'

	for page in [1, 2]:
		response = requests.get(board_link_format.format(page))
		soup = BeautifulSoup(response.text, 'lxml')

		anchors = soup.select('#contents > ol > li > a')
		for line in anchors:
			lines.append(line)

	for line in lines:
		parsed = parse_qs(urlparse(line.attrs['href']).query, keep_blank_values=True)

		message_id = parsed['messageId'][0]
		title = line.text

		if session.query(UniversityNoticeModel).filter(UniversityNoticeModel.id == message_id).first() is not None:
			continue

		new_model = UniversityNoticeModel(id=message_id, type='main', title=title)
		session.add(new_model)

		attachments = [
			create_link_message('학교 전체 공지사항', title, new_model.document_link)
		]

		slack.chat.post_message(broadcast_channel, None, username=bot_name, attachments=attachments)

	session.commit()
