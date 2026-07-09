### Project setup

    # Use this directory as the project root

### run below commands to build image and run container :

    cd jwt-authentication
    docker build -t todo-image .
    docker run -p 8000:8000 --env-file .env --name todo-container todo-image

# API documentation

### app/api

- This contains four files for different routers.

    1. auth route : This route is responsible for user registration, verification, login, and logout.

    2. tasks route : This route is responsible for creating, updating, deleting, and fetching tasks. All routes in this router are protected and require access token for authorization.

    3. users route : This route gets access token form header and allows usr to get their info. it also has endpoint which is admin only and allows admin to get all users info.

#### app/core

- This contains three files.

    1. config.py : This file contains setting class which has environment variables from .env file so we can use this setting class for confidential values.

    2. dependencies.py : This file contains all the dependencies for the project. It has functions for getting database session, getting current user.

    3. security.py : This file contains all the security related functions like hashing password, verifying password, creating access token and creating refresh token.

#### app/db

- This contains two files.

    1. base.py : This file contains the base class for the database models.

    2. session.py : This file contains session factory to get session to interact with database.

#### app/models

- This contains two files.

- Entity Relation diagram for this is show below.

<img src = "jwt-authentication-erd.png" alt = "ERD" width = "500" height = "300"/>

    - Users table : This table contains all the info. of users.

    - Tasks table : This table contains all the info. of tasks. It has foreign key to users table.

    - RefreshTokens table : This table contains all the refresh tokens. It has foreign key to users table.

#### app/repositories

- This contains all the database queries for the project. It has two files.

    1. task_repository.py : This file contains all the database queries related to tasks.

    2. user_repository.py : This file contains all the database queries related to users and refresh tokens.

#### app/schemas

- This contains all the pydantic schemas for the project. It has three files.

    1. task.py : This file contains all the pydantic schemas related to tasks.

    2. user.py : This file contains all the pydantic schemas related to users and refresh tokens.

    3. token.py : This file contains all the pydantic schemas related to token and token data.

#### app/services

- This contains all the business logic for the project.

### IMPORTANT TOPICS :

- Refresh token :

    Firstly we check if refresh token is valid or not by verifying it with database and then we check if it is expired or not by checking current time with expiry time. If both are valid then we create new access token and refresh token and  return it to user.

- Account lock mechanism :

    Here we are storing failed login attempts in redis. If user tries to login with wrong credentials then we increment the failed login attempts in redis. If failed login attempts are more than or equal to 5 then we lock the account for 10 minutes by setting a key(user's email) in redis with expiry time of 10 minutes. If user tries to login while account is locked then we return error message that account is locked.


- Rate limiting :

    Here we are using Token Bucket algorithm to prevent API abuse by controlling request flow based on client IP addresses. It uses a "bucket" strategy where each user starts with a set number of tokens (10 by default), with every request consuming exactly one. Tokens are automatically replenished over time at a defined refill rate (1 per second), allowing users to perform short bursts of activity while maintaining a strict long-term average. If a user exhausts their bucket, the middleware intercepts the request and returns a 429 Too Many Requests response until enough time has passed for the bucket to refill. This implementation is lightweight, calculating refills on-the-fly during the request lifecycle without requiring background workers.

### Short documentation explaining

[click here]
(https://docs.google.com/document/d/1UApfVx70lPusnnz6jdcVuhvWLXVwNcqy0zEY-1Vi8HI/edit?usp=sharing)
