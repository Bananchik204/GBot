from peewee import *
from pathlib import Path

Path("db").mkdir(exist_ok=True)
database = SqliteDatabase("db/data.db")
database.connect()

class BaseModel(Model):
	class Meta:
		db = database

class Boss(BaseModel):
	class Meta:
		db_table = 'Bosses'

	name = CharField(max_length=500)
	health = IntegerField()

	def add_boss(name: str, health: int):
		try:
			boss = [x for x in Boss.select().where(Boss.name == name)]

			boss.name = name
			boss.health = health

			return boss.save()
		except:
			pass

		return Boss.create(name=name, health=health)

	def get_boss(name: str):
		return [x for x in Boss.select().where(Boss.name == name)]

	def update_boss(name: str, type: str, value: int):
		boss = Boss.get_boss(name=name)

		if type == "health":
			boss.health = value

if __name__ == "__main__":
	db.create_tables([Boss])