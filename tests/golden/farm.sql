CREATE EXTENSION IF NOT EXISTS "btree_gist";

CREATE SCHEMA "buildings";

CREATE SCHEMA "herd";

CREATE TABLE "buildings"."barns"(
	"barnid" uuid NOT NULL,
	"barnname" text NOT NULL,
	"capacity" integer NOT NULL,
	"built" date,
	CONSTRAINT "barns_pk" PRIMARY KEY ("barnid"),
	CONSTRAINT "barns_name_unique" UNIQUE ("barnname"),
	CONSTRAINT "barns_capacity_positive" CHECK (capacity >= 0)
	);

COMMENT ON TABLE "buildings"."barns" IS 'One row per barn.';

COMMENT ON CONSTRAINT "barns_pk" ON "buildings"."barns" IS 'Barns are identified by barnid.';

COMMENT ON CONSTRAINT "barns_name_unique" ON "buildings"."barns" IS 'No two barns share a name.';

COMMENT ON CONSTRAINT "barns_capacity_positive" ON "buildings"."barns" IS 'Capacity can''t be negative.';

CREATE TABLE "buildings"."pens"(
	"barnid" uuid NOT NULL,
	"penid" smallint NOT NULL,
	CONSTRAINT "pens_pk" PRIMARY KEY ("barnid", "penid")
	);

COMMENT ON TABLE "buildings"."pens" IS 'Pens inside a barn.';

COMMENT ON CONSTRAINT "pens_pk" ON "buildings"."pens" IS 'A pen is identified by its barn and its number.';

CREATE TABLE "herd"."cows"(
	"cowid" uuid NOT NULL,
	"eartag" character(8),
	"born" timestamp with time zone NOT NULL,
	"damid" uuid,
	"barnid" uuid,
	"penid" smallint,
	"nicknames" text[],
	"extra" jsonb,
	CONSTRAINT "cows_pk" PRIMARY KEY ("cowid"),
	CONSTRAINT "cows_eartag_unique" UNIQUE NULLS NOT DISTINCT ("eartag"),
	CONSTRAINT "cows_not_own_dam" CHECK (damid IS DISTINCT FROM cowid)
	);

COMMENT ON TABLE "herd"."cows" IS 'One row per cow.';

COMMENT ON CONSTRAINT "cows_pk" ON "herd"."cows" IS 'Cows are identified by cowid.';

COMMENT ON CONSTRAINT "cows_eartag_unique" ON "herd"."cows" IS 'Ear tags are unique, and only one cow can lack one.';

COMMENT ON CONSTRAINT "cows_not_own_dam" ON "herd"."cows" IS 'A cow can''t be her own mother.';

CREATE TABLE "herd"."pen_stays"(
	"cowid" uuid NOT NULL,
	"barnid" uuid NOT NULL,
	"penid" smallint NOT NULL,
	"arrived" timestamp with time zone NOT NULL,
	"departed" timestamp with time zone,
	CONSTRAINT "pen_stays_pk" PRIMARY KEY ("cowid", "arrived"),
	CONSTRAINT "pen_stays_no_overlap" EXCLUDE USING gist (cowid WITH =, tstzrange(arrived, departed) WITH &&)
	);

COMMENT ON TABLE "herd"."pen_stays" IS 'Which pen a cow was in, and when.';

COMMENT ON CONSTRAINT "pen_stays_pk" ON "herd"."pen_stays" IS 'One stay per cow per start time.';

COMMENT ON CONSTRAINT "pen_stays_no_overlap" ON "herd"."pen_stays" IS 'A cow can''t be in two pens at once.';

CREATE INDEX pens_penid_idx ON buildings.pens (penid);

COMMENT ON INDEX "buildings"."pens_penid_idx" IS 'Look up pens by number across barns.';

CREATE INDEX cows_born_idx ON herd.cows (born);

COMMENT ON INDEX "herd"."cows_born_idx" IS 'Find cows by age.';

ALTER TABLE "buildings"."pens" ADD CONSTRAINT "pens_barn_fk" FOREIGN KEY ("barnid") REFERENCES "buildings"."barns" ("barnid") ON DELETE CASCADE ON UPDATE CASCADE;

COMMENT ON CONSTRAINT "pens_barn_fk" ON "buildings"."pens" IS 'Pens go when their barn goes.';

ALTER TABLE "herd"."cows" ADD CONSTRAINT "cows_dam_fk" FOREIGN KEY ("damid") REFERENCES "herd"."cows" ("cowid") ON DELETE SET NULL;

COMMENT ON CONSTRAINT "cows_dam_fk" ON "herd"."cows" IS 'Losing the dam''s record keeps the calf.';

ALTER TABLE "herd"."cows" ADD CONSTRAINT "cows_pen_fk" FOREIGN KEY ("barnid", "penid") REFERENCES "buildings"."pens" ("barnid", "penid");

COMMENT ON CONSTRAINT "cows_pen_fk" ON "herd"."cows" IS 'The pen the cow is in.';

ALTER TABLE "herd"."pen_stays" ADD CONSTRAINT "pen_stays_cow_fk" FOREIGN KEY ("cowid") REFERENCES "herd"."cows" ("cowid");

COMMENT ON CONSTRAINT "pen_stays_cow_fk" ON "herd"."pen_stays" IS 'The cow must exist.';
