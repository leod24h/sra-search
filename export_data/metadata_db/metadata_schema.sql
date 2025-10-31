--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4 (Ubuntu 17.4-1.pgdg20.04+2)
-- Dumped by pg_dump version 17.4 (Ubuntu 17.4-1.pgdg20.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metadata (
    acc text,
    experiment text,
    biosample text,
    organism text,
    organism_id text,
    bioproject text,
    releasedate bigint,
    collectiondate double precision,
    center_name text,
    country text,
    country_northeast_lat double precision,
    country_northeast_lng double precision,
    country_southwest_lat double precision,
    country_southwest_lng double precision,
    latitude double precision,
    longitude double precision,
    attribute text,
    instrument text,
    assay_type text,
    consent text,
    librarylayout text,
    libraryselection text,
    librarysource text,
    platform text,
    mbytes double precision,
    mbases double precision,
    avgspotlen double precision,
    insertsize double precision,
    library_name text,
    biosamplemodel_sam text,
    sample_name_sam text,
    id integer NOT NULL,
    vec public.halfvec(384),
    sra_study text
);


ALTER TABLE public.metadata OWNER TO postgres;

--
-- Name: metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metadata_id_seq OWNER TO postgres;

--
-- Name: metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metadata_id_seq OWNED BY public.metadata.id;


--
-- Name: metadata id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metadata ALTER COLUMN id SET DEFAULT nextval('public.metadata_id_seq'::regclass);


--
-- Name: metadata metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metadata
    ADD CONSTRAINT metadata_pkey PRIMARY KEY (id);


--
-- Name: idx_acc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_acc ON public.metadata USING btree (acc);


--
-- Name: idx_bioproject; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bioproject ON public.metadata USING btree (bioproject);


--
-- Name: idx_biosample; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biosample ON public.metadata USING btree (biosample);


--
-- Name: idx_collectiondate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collectiondate ON public.metadata USING btree (collectiondate);


--
-- Name: idx_collectionreleasedate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collectionreleasedate ON public.metadata USING btree (releasedate, collectiondate);


--
-- Name: idx_experiment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_experiment ON public.metadata USING btree (experiment);


--
-- Name: idx_organism_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_organism_id ON public.metadata USING btree (organism_id);


--
-- Name: idx_releasedate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_releasedate ON public.metadata USING btree (releasedate);


--
-- Name: idx_sra_study; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sra_study ON public.metadata USING btree (sra_study);


--
-- Name: metadata_lower_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX metadata_lower_idx ON public.metadata USING gin (lower(country) public.gin_trgm_ops);


--
-- Name: metadata_vec_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX metadata_vec_idx ON public.metadata USING ivfflat (vec public.halfvec_cosine_ops) WITH (lists='800');


--
-- PostgreSQL database dump complete
--

