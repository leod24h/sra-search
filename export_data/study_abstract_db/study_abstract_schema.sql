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
-- Name: study_abstract; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_abstract (
    sra_study text NOT NULL,
    study_title text,
    study_abstract text,
    center_project_name text,
    study_type text,
    text text,
    vec public.halfvec(384)
);


ALTER TABLE public.study_abstract OWNER TO postgres;

--
-- Name: study_abstract study_abstract_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_abstract
    ADD CONSTRAINT study_abstract_pkey PRIMARY KEY (sra_study);


--
-- Name: study_abstract_to_tsvector_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX study_abstract_to_tsvector_idx ON public.study_abstract USING gin (to_tsvector('english'::regconfig, study_title));


--
-- Name: study_abstract_vec_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX study_abstract_vec_idx ON public.study_abstract USING ivfflat (vec public.halfvec_cosine_ops) WITH (lists='500');


--
-- PostgreSQL database dump complete
--

