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
-- Name: taxonomy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxonomy (
    tax_id bigint NOT NULL,
    parent_tax_id bigint,
    rank character varying(50),
    scientific_name character varying(255),
    common_name character varying(255),
    genbank_common_name character varying(255),
    synonym character varying(255),
    children_ids text,
    library_index character varying(245),
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, (((((((COALESCE(scientific_name, ''::character varying))::text || ' '::text) || (COALESCE(common_name, ''::character varying))::text) || ' '::text) || (COALESCE(genbank_common_name, ''::character varying))::text) || ' '::text) || (COALESCE(synonym, ''::character varying))::text))) STORED
);


ALTER TABLE public.taxonomy OWNER TO postgres;

--
-- Name: taxonomy taxonomy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy
    ADD CONSTRAINT taxonomy_pkey PRIMARY KEY (tax_id);


--
-- Name: idx_search_vector; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_search_vector ON public.taxonomy USING gin (search_vector);


--
-- PostgreSQL database dump complete
--

