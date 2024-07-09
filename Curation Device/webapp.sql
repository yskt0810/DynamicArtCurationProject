--
-- PostgreSQL database dump
--

-- Dumped from database version 13.14 (Debian 13.14-0+deb11u1)
-- Dumped by pg_dump version 13.14 (Debian 13.14-0+deb11u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: devices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices (
    device_id integer NOT NULL,
    device_name text,
    description text,
    token text
);


--
-- Name: devices_device_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.devices_device_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: devices_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.devices_device_id_seq OWNED BY public.devices.device_id;


--
-- Name: facecount_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.facecount_log (
    logid integer NOT NULL,
    date date,
    "time" time without time zone,
    session_facecount_id integer,
    duration double precision,
    archive text,
    artid bigint,
    serial_num text,
    filename text,
    log_filename text,
    device_id integer
);


--
-- Name: facecount_log_logid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.facecount_log_logid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: facecount_log_logid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.facecount_log_logid_seq OWNED BY public.facecount_log.logid;


--
-- Name: test; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test (
    id integer,
    name text
);


--
-- Name: devices device_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices ALTER COLUMN device_id SET DEFAULT nextval('public.devices_device_id_seq'::regclass);


--
-- Name: facecount_log logid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.facecount_log ALTER COLUMN logid SET DEFAULT nextval('public.facecount_log_logid_seq'::regclass);


--
-- PostgreSQL database dump complete
--

