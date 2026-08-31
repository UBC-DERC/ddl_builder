# DDL Builder

Given a database, defined using the YAML template in the `data_model` repository, the DDL Builder repository
is designed to create the database DDL (the SQL definition of the database structure). The goal of this repository is to provide a testing
environment for our data models, and to help provide a toolset to manage ongoing changes to the database as the data model evolves over time.

## DDL Workflow

When a change is made to the data model, and that change is approved through a push to the `production` or `devel` branch (the change has been suggested and vetted), then a GitHub action will trigger the workflow in this repository, pulling the Docker container, creating the database and adding extensions, and then building the schema and tables as defiined by the YAML files within `data_model`. A sample of [a valid yaml file](./examples/output.yaml) is found in the [`examples` folder](./examples/).

On a successful run this repository will return a signal that indicates the data model is clear, no errors exist and that all references and indexes function as expected. Based on this, the database itself would be ready to deploy to a production environment.

```bash
uv run ddl-builder ./examples/output.yaml -o examples/ddl_model.yaml -d examples/docs
```

```mermaid
flowchart LR
    output@{ shape: doc, label: "Output Document" }
    subgraph data_model
        direction TB
        modelupdate@{ shape: rounded, label: "Data Model Update" }
        ghPush@{ shape: trap-t, label: "GitHub Push (data_model)" }
        ghActions@{ shape: process, label: "GitHub Actions"}

        modelupdate --"Approved Update" --> ghPush
        ghPush --"Actions Trigger"--> ghActions
    end
    subgraph ddl_builder
        docker@{ shape: docs, label: "Docker Compose" }
        subgraph Container
        d3db@{ shape: cyl, label: "Dairy Database" }
        ddlPy@{ shape: process, label: "DDL Builder" }
        end
    end

    ghActions --> docker
    docker --> Container
    ddlPy --"Programmatic CREATE"--> d3db
    d3db --> output

```

At the end of deployment we should have a database (that can be created and destroyed) that has been built without errors, and a log of the build process written to the user's directory.

## Class Structure

The package uses a structure similar to SQLAlchemy, with individual classes for tables, schema, the database, indexes, etc. Where this differs from SQLAlchemy is that this project aims only to convert classes into Postgres-specific SQL, and to structure calls in a way that we support valid deployment of the SQL to an existing server.

```mermaid
---
title: ddl_builder
---
classDiagram
    class Server{
        +str dbname
        +int port
        +str user
        +str password
        +str host
        +psycopg.Connection conn
        +connect()
        +check()
        +conn_string()
        +close()
    }
    class D3Database{
        +str name
        +str comment
        +list[Schema] schemas
        +database_clause()
        +extension_clause()
    }
    class Schema{
        +str name
        +str comment
        +list[Table] tables
        +list[Index] indexes
        +list[Constraint] constraints
        +schema_clause()
    }
    Schema-->D3Database
    class Table{
        +str name
        +str type
        +str comment
        +list[Column] columns
        +table_clause()
    }
    Table-->Schema
    class Column{
        +str name
        +str type
        +str comment
        +bool nullable
        +column_clause()
    }
    Column-->Table
    class Index{
        +str name
        +str comment
        +str type
        +str definition
        +list[Reference] reference
        +index_clause()
    }
    Reference-->Index
    Index-->Schema
    class Constraint{
        +str definition
        +str name
        +str comment
        +enum type
        +Reference reference
        +constraint_clause()
    }
    class Reference{
        +str table
        +str column
    }
    Constraint<--Reference
    Constraint-->Schema
```

The nested classes do not explicitly link, except through the `Reference` class and through membership in the various lists. So, for instance, an `Index` class does not *know* of the presence of a particular table within the same scema. We do perform validation throughout however, to check whether or not tables are present, or if constraints are linked.

## Testing

Tests use `pytest` with an HTML report written to `docs/test_report.html` to provide ongoing oversight of the project and potential issues. We use `pydantic` for class and variable validation throughout, to ensure that error messages and data validation tests can be run effectively on all methods and classes.

## Quick Start

Given the example file, we can build valid SQL using the command:

```
uv run ddl_builder
```