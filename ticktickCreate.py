from ticktick.api import TickTickClient  # Main Interface
from ticktick.oauth2 import OAuth2  # OAuth2 Manager
# 用户数据
client_id = ""
client_secret = ""
uri = ""
username = ""
password = ""

auth_client = OAuth2(client_id=client_id,
                     client_secret=client_secret,
                     redirect_uri=uri)

client = TickTickClient(username, password, auth_client)


def send(title, con, time):
    events = client.get_by_fields(name='作业', search='projects')

    events_id = events['id']
    reminders = ["TRIGGER:-P0DT12H0M0S"]
    task = client.task.builder(title,
                               startDate=time,
                               dueDate=time,
                               content=con,
                               projectId=events_id,
                               reminders=reminders)

    result = client.task.create(task)
    return result


def get(title):
    task = client.get_by_fields(title=title, search="tasks")
    return task


def update(title, content):
    task = client.get_by_fields(title=title, search="tasks")
    task['content'] = content
    client.task.update(task)


if __name__ == '__main__':
    a = get("unclutter")
    print(a)
