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
-- Name: geo_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.geo_info (
    location text NOT NULL,
    loc_lat double precision,
    loc_lng double precision,
    northeast_lat double precision,
    northeast_lng double precision,
    southwest_lat double precision,
    southwest_lng double precision
);


ALTER TABLE public.geo_info OWNER TO postgres;

--
-- Name: geo_info geo_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geo_info
    ADD CONSTRAINT geo_info_pkey PRIMARY KEY (location);


--
-- Name: idx_geo_info_location_lower_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_geo_info_location_lower_trgm ON public.geo_info USING gin (lower(location) public.gin_trgm_ops);


--
-- PostgreSQL database dump complete
--

