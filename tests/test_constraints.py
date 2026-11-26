import pytest

from ddl_builder import Constraint, Reference

def test_check_constraint_no_ddl_fails():
    with pytest.raises(ValueError):
        Constraint(name="check",
                   type="CHECK",
                   comment="Peanut",
                   columns=["bonus"])


def test_exclude_constraint_no_ddl_fails():
    with pytest.raises(ValueError):
        Constraint(name="check",
                   type="EXCLUDE",
                   comment="Peanut",
                   columns=["bonus"])

def test_pk_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="PRIMARY KEY",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" PRIMARY KEY ("first", "second")'

def test_pk_constraint_one_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="PRIMARY KEY",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" PRIMARY KEY ("first")'

def test_unique_constraint_one_column_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE ("first")'


def test_unique_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE ("first", "second")'


def test_unique_nn_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE NULLS NOT DISTINCT",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE NULLS NOT DISTINCT ("first", "second")'

def test_check_constraint_with_ddl_passes():
    cstr = Constraint(name="check",
                      type="CHECK",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl="CHECK (bonus > 100)")
    assert cstr.constraint_clause().as_string() == f'CONSTRAINT \"check\" {cstr.ddl}'


def test_exclude_constraint_with_ddl_passes_leading_constraint():
    cstr = Constraint(name="exclude",
                      type="EXCLUDE",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl="CONSTRAINT exclude EXCLUDE (bonus < 100)")
    assert cstr.constraint_clause().as_string() == "CONSTRAINT \"exclude\" EXCLUDE (bonus < 100)"

def test_exclude_constraint_with_ddl_passes_leading_constraint_doublespaced():
    cstr = Constraint(name="exclude",
                      type="EXCLUDE",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl="CONSTRAINT  exclude EXCLUDE (bonus < 100)")
    assert cstr.constraint_clause().as_string() == "CONSTRAINT \"exclude\" EXCLUDE (bonus < 100)"

def test_exclude_constraint_with_ddl_passes_leading_constraint_quoted():
    cstr = Constraint(name="exclude",
                      type="EXCLUDE",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl='CONSTRAINT "exclude" EXCLUDE (bonus < 100)')
    assert cstr.constraint_clause().as_string() == "CONSTRAINT \"exclude\" EXCLUDE (bonus < 100)"

def test_exclude_constraint_with_ddl_wrong_name_fails():
    cstr = Constraint(name="exclude",
                      type="EXCLUDE",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl='CONSTRAINT "preclude" EXCLUDE (bonus < 100)')
    with pytest.raises(ValueError):
            cstr.constraint_clause()


def test_foreign_key_constraint_clause_fails():
    cstr = Constraint(name="exclude",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["bonus"],
                      references=Reference(table="banana", columns=["one"]),
                      ddl="CONSTRAINT exclude EXCLUDE (bonus < 100)")
    with pytest.raises(ValueError):
        cstr.constraint_clause()

def test_fk_alter_table_clause_on_primary_key_fails():
    cstr = Constraint(name="cows_pk",
                      type="PRIMARY KEY",
                      comment="Peanut",
                      columns=["cowid"])
    with pytest.raises(ValueError):
        cstr.fk_alter_table_clause(schema="farm", table="cows")


def test_fk_alter_table_clause_same_schema():
    cstr = Constraint(name="cows_barn_fk",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["barnid"],
                      references=Reference(table="barns", columns=["barnid"]))
    clause = cstr.fk_alter_table_clause(schema="farm", table="cows")
    assert clause.as_string() == (
        'ALTER TABLE "farm"."cows" ADD CONSTRAINT "cows_barn_fk" '
        'FOREIGN KEY ("barnid") REFERENCES "farm"."barns" ("barnid")'
    )


def test_fk_alter_table_clause_other_schema_composite():
    cstr = Constraint(name="cows_pen_fk",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["barnid", "penid"],
                      references=Reference(schema="buildings",
                                           table="pens",
                                           columns=["barnid", "penid"]))
    clause = cstr.fk_alter_table_clause(schema="farm", table="cows")
    assert clause.as_string() == (
        'ALTER TABLE "farm"."cows" ADD CONSTRAINT "cows_pen_fk" '
        'FOREIGN KEY ("barnid", "penid") REFERENCES "buildings"."pens" ("barnid", "penid")'
    )

def test_fk_alter_table_clause_on_delete():
    cstr = Constraint(name="cows_barn_fk",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["barnid"],
                      references=Reference(table="barns",
                                           columns=["barnid"],
                                           on_delete="CASCADE"))
    clause = cstr.fk_alter_table_clause(schema="farm", table="cows")
    assert clause.as_string() == (
        'ALTER TABLE "farm"."cows" ADD CONSTRAINT "cows_barn_fk" '
        'FOREIGN KEY ("barnid") REFERENCES "farm"."barns" ("barnid") '
        'ON DELETE CASCADE'
    )


@pytest.mark.parametrize("action", ["NO ACTION", "RESTRICT", "CASCADE", "SET NULL", "SET DEFAULT"])
def test_fk_alter_table_clause_on_delete_and_update(action):
    cstr = Constraint(name="cows_barn_fk",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["barnid"],
                      references=Reference(table="barns",
                                           columns=["barnid"],
                                           on_delete=action,
                                           on_update=action))
    clause = cstr.fk_alter_table_clause(schema="farm", table="cows")
    assert clause.as_string().endswith(f" ON DELETE {action} ON UPDATE {action}")


def test_reference_bad_action_fails():
    with pytest.raises(ValueError):
        Reference(table="barns", columns=["barnid"], on_delete="DROP TABLE cows")

def test_constraint_reference_without_table_fails():
    # ddlml rejects this when the model is built, so fk_alter_table_clause never sees it.
    with pytest.raises(ValueError):
        Constraint(name="cows_barn_fk",
                   type="FOREIGN KEY",
                   comment="Peanut",
                   columns=["barnid"],
                   references=Reference(columns=["barnid"]))