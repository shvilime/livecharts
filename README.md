Сервис состоит из двух частей:
- Backend, написан на python на фреймворке [FastApi](https://fastapi.tiangolo.com/) .
- Frontend, написан на typescript как SPA на фреймворке [Quasar](https://quasar.dev/) с Vue под капотом.

В целом структуру приложения можно представить в следующем виде:
```plantuml
@startuml

object WebServer
WebServer : name = Nginx

package Service <<cloud>> {
   object Frontend
   Frontend : framework: Quasar
   Frontend : type: SPA

   object Backend
   Backend : framework: FastApi
   Backend : type: async
}

package Storages <<cloud>> {
  object Database
  Database : name: Postgres

  object Cache
  Cache : name: Redis
}

WebServer-r->Frontend
WebServer-r->Backend

Backend-d->Database : Movement
Database-d->Backend : History\ndata
Backend-d->Cache : Movement
Cache-u->Backend : Last\nquote

Frontend<-d->Backend : Websocket\nLive data
Frontend<-d->Backend : Requests\nHistory quotes

@enduml
```

В качестве БД, для хранения исторических данных, использована база данных Postgres.
Redis использовался для хранения текущих котировок и быстрой генерации live данных для frontend.
Для будущего распределения нагрузки frontend и backend прикрыты nginx.
За работоспособность backend отвечает supervisor, использованный в качестве менеджера процессов.
