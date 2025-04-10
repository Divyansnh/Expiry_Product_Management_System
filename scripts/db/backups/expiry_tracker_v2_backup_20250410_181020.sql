--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Homebrew)
-- Dumped by pg_dump version 14.17 (Homebrew)

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: divyanshsingh
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO divyanshsingh;

--
-- Name: items; Type: TABLE; Schema: public; Owner: divyanshsingh
--

CREATE TABLE public.items (
    name character varying(100) NOT NULL,
    description text,
    quantity double precision,
    unit character varying(20),
    batch_number character varying(50),
    purchase_date timestamp without time zone,
    expiry_date timestamp without time zone,
    purchase_price double precision,
    selling_price double precision,
    cost_price double precision,
    discounted_price double precision,
    location character varying(100),
    notes text,
    image_url character varying(255),
    status_changed_at timestamp without time zone,
    status character varying(20),
    user_id integer NOT NULL,
    zoho_item_id character varying(100),
    id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.items OWNER TO divyanshsingh;

--
-- Name: items_id_seq; Type: SEQUENCE; Schema: public; Owner: divyanshsingh
--

CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.items_id_seq OWNER TO divyanshsingh;

--
-- Name: items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: divyanshsingh
--

ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: divyanshsingh
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    item_id integer,
    message character varying(255) NOT NULL,
    type character varying(50) NOT NULL,
    priority character varying(10),
    is_read boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(20)
);


ALTER TABLE public.notifications OWNER TO divyanshsingh;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: divyanshsingh
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO divyanshsingh;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: divyanshsingh
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: divyanshsingh
--

CREATE TABLE public.reports (
    user_id integer NOT NULL,
    date date NOT NULL,
    total_items integer,
    total_value double precision,
    expiring_items integer,
    expired_items integer,
    low_stock_items integer,
    total_sales double precision,
    total_purchases double precision,
    report_data json,
    is_public boolean,
    public_token character varying(64),
    id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.reports OWNER TO divyanshsingh;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: divyanshsingh
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reports_id_seq OWNER TO divyanshsingh;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: divyanshsingh
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: divyanshsingh
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256),
    password_reset_token character varying(256),
    is_active boolean,
    is_admin boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone,
    notification_preferences json,
    verification_code character varying(32),
    verification_code_expires_at timestamp without time zone,
    is_verified boolean,
    email_notifications boolean,
    sms_notifications boolean,
    in_app_notifications boolean,
    zoho_client_id character varying(255),
    zoho_client_secret character varying(255),
    zoho_access_token character varying(255),
    zoho_refresh_token character varying(255),
    zoho_token_expires_at timestamp without time zone,
    zoho_organization_id character varying(255),
    password_reset_token_expires_at timestamp without time zone,
    login_attempts integer DEFAULT 0,
    locked_until timestamp without time zone
);


ALTER TABLE public.users OWNER TO divyanshsingh;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: divyanshsingh
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO divyanshsingh;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: divyanshsingh
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: items id; Type: DEFAULT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: divyanshsingh
--

COPY public.alembic_version (version_num) FROM stdin;
bdaddb1d9553
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: divyanshsingh
--

COPY public.items (name, description, quantity, unit, batch_number, purchase_date, expiry_date, purchase_price, selling_price, cost_price, discounted_price, location, notes, image_url, status_changed_at, status, user_id, zoho_item_id, id, created_at, updated_at) FROM stdin;
Blue Label	Whiskey	10	pcs	\N	\N	2026-10-08 00:00:00	0	185	165	\N	\N	\N	\N	2025-04-08 19:17:48.285513	active	2	740413000000100171	40	2025-04-07 20:58:46.844321	2025-04-08 18:42:24.059679
Corneto Chocolate	Ice cream	135	pcs	\N	\N	2025-12-31 00:00:00	\N	4.5	3.5	\N	\N	\N	\N	2025-04-10 15:27:57.055474	active	2	740413000000104008	52	2025-04-08 10:39:11.472003	2025-04-10 14:27:57.056285
Dairy milk	chocolate	5	box	\N	\N	2025-04-09 00:00:00	\N	4.5	3.5	\N	\N	\N	\N	2025-04-10 15:27:57.353753	expired	2	740413000000079214	84	2025-04-08 22:08:09.985067	2025-04-10 14:27:57.354416
CheeseCake	Cake	135	pcs	\N	\N	2025-06-27 00:00:00	\N	3.5	2.5	\N	\N	\N	\N	2025-04-08 23:05:47.218102	active	2	740413000000096012	82	2025-04-08 22:05:34.878197	2025-04-10 11:11:52.961681
Test Item 30 Days	\N	10	\N	\N	\N	2025-05-08 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	71	2025-04-08 16:28:38.541182	2025-04-08 16:28:38.541185
Test Item 15 Days	\N	10	\N	\N	\N	2025-04-23 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	72	2025-04-08 16:28:38.54494	2025-04-08 16:28:38.544942
Test Item 7 Days	\N	10	\N	\N	\N	2025-04-15 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	73	2025-04-08 16:28:38.546524	2025-04-08 16:28:38.546525
Test Item 3 Days	\N	10	\N	\N	\N	2025-04-11 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	74	2025-04-08 16:28:38.548059	2025-04-08 16:28:38.54806
Test Item 1 Day	\N	10	\N	\N	\N	2025-04-09 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	75	2025-04-08 16:28:38.549772	2025-04-08 16:28:38.549775
Test Item 4 Days	\N	10	\N	\N	\N	2025-04-12 00:00:00	\N	\N	\N	\N	\N	\N	\N	\N	Pending Expiry Date	8	\N	76	2025-04-08 16:28:38.551667	2025-04-08 16:28:38.551669
Smirnoff (1L)	Vodka	3	box	\N	\N	2025-04-10 00:00:00	\N	10.99	9.99	\N	\N	\N	\N	2025-04-10 15:27:56.847636	expired	2	740413000000100228	47	2025-04-07 22:18:28.011543	2025-04-10 14:27:56.848255
Bacon Sandwich	Sandwich	35	pcs	\N	\N	2025-04-16 00:00:00	\N	3.5	2.5	\N	\N	\N	\N	2025-04-09 00:06:55.777111	expiring_soon	2	740413000000101226	80	2025-04-08 22:03:17.716969	2025-04-08 23:06:55.778303
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: divyanshsingh
--

COPY public.notifications (id, user_id, item_id, message, type, priority, is_read, created_at, updated_at, status) FROM stdin;
33	2	\N	Warning: Product Doritos (ID: 48) expires in 3 days!	in_app	high	f	2025-04-08 17:31:27.032935	2025-04-08 18:45:53.91036	pending
34	8	71	Info: Product Test Item 30 Days (ID: 71) expires in 30 days.	in_app	low	f	2025-04-08 17:28:38.599904	2025-04-08 16:28:38.599906	pending
35	8	72	Info: Product Test Item 15 Days (ID: 72) expires in 15 days.	in_app	low	f	2025-04-08 17:28:38.602471	2025-04-08 16:28:38.602473	pending
36	8	73	Notice: Product Test Item 7 Days (ID: 73) expires in 7 days.	in_app	normal	f	2025-04-08 17:28:38.604518	2025-04-08 16:28:38.604519	pending
37	8	74	Warning: Product Test Item 3 Days (ID: 74) expires in 3 days!	in_app	high	f	2025-04-08 17:28:38.606569	2025-04-08 16:28:38.60657	pending
38	8	75	Critical: Product Test Item 1 Day (ID: 75) expires tomorrow!	in_app	high	f	2025-04-08 17:28:38.608594	2025-04-08 16:28:38.608595	pending
27	2	\N	Item 'Mini Cheddars' is expiring in 1 days	expiry	medium	f	2025-04-07 23:59:10.509243	2025-04-08 16:31:59.94602	pending
29	2	\N	Item 'Mini Cheddars' has expired	expiry	high	f	2025-04-08 00:01:54.435015	2025-04-08 16:31:59.946021	pending
30	2	47	Item 'Smirnoff (1L)' is expiring in 2 days	expiry	medium	f	2025-04-08 00:41:22.998128	2025-04-08 16:31:59.946021	pending
92	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 11:54:18.527798	2025-04-10 10:54:18.527802	pending
93	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 11:54:18.710107	2025-04-10 10:54:18.710111	pending
94	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 11:54:18.889502	2025-04-10 10:54:18.889504	pending
39	2	\N	Item 'CheeseCake' is expiring in 3 days	expiry	medium	f	2025-04-08 17:41:00.551869	2025-04-08 19:39:12.430767	pending
41	2	\N	Warning: Product CheeseCake (ID: 77) expires in 3 days!	in_app	high	f	2025-04-08 18:31:27.020501	2025-04-08 19:39:12.430773	read
43	2	\N	Critical: Product Monster Energy Drinks (ID: 32) expires tomorrow!	in_app	high	f	2025-04-08 18:31:27.030397	2025-04-08 19:39:48.658348	read
44	2	52	Item 'Corneto Chocolate' is expiring in 1 days	expiry	medium	f	2025-04-08 20:40:27.790573	2025-04-08 19:40:27.795325	pending
40	2	\N	Item 'Mini Eggs' is expiring in 3 days	expiry	medium	f	2025-04-08 17:42:57.164702	2025-04-08 19:40:51.020069	pending
42	2	\N	Warning: Product Mini Eggs (ID: 78) expires in 3 days!	in_app	high	f	2025-04-08 18:31:27.027795	2025-04-08 19:40:51.020076	read
45	2	84	Item 'Dairy milk' is expiring in 1 days	expiry	medium	f	2025-04-08 23:08:11.028078	2025-04-08 22:08:11.028084	pending
46	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 00:06:55.319766	2025-04-08 23:06:55.319776	pending
47	2	80	Item 'Bacon Sandwich' is expiring in 7 days	expiry	medium	f	2025-04-09 00:06:55.779276	2025-04-08 23:06:55.779282	pending
48	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 00:06:56.002678	2025-04-08 23:06:56.00268	pending
49	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 00:16:53.92997	2025-04-08 23:16:53.929975	pending
50	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 00:16:54.148203	2025-04-08 23:16:54.148208	pending
51	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 00:50:26.660269	2025-04-08 23:50:26.660282	pending
52	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 00:50:26.888434	2025-04-08 23:50:26.888439	pending
53	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 00:50:30.266143	2025-04-08 23:50:30.266148	pending
54	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 00:50:30.471635	2025-04-08 23:50:30.47164	pending
55	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 06:37:37.491522	2025-04-09 05:37:37.491531	pending
56	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 06:37:37.684453	2025-04-09 05:37:37.684458	pending
57	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 06:39:31.491466	2025-04-09 05:39:31.491473	pending
58	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 06:39:31.711644	2025-04-09 05:39:31.711651	pending
59	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-09 10:53:46.62928	2025-04-09 09:53:46.629286	pending
60	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-09 10:53:46.828498	2025-04-09 09:53:46.828503	pending
61	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:28:36.467827	2025-04-10 09:28:36.467839	pending
62	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:28:44.552853	2025-04-10 09:28:44.552857	pending
63	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:28:44.769742	2025-04-10 09:28:44.76975	pending
64	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:28:45.010261	2025-04-10 09:28:45.010267	pending
65	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:36:55.368901	2025-04-10 09:36:55.368904	pending
66	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:36:55.619888	2025-04-10 09:36:55.619893	pending
67	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:36:55.815731	2025-04-10 09:36:55.815736	pending
68	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:46:27.510025	2025-04-10 09:46:27.510029	pending
69	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:46:27.748539	2025-04-10 09:46:27.748542	pending
70	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:46:27.947872	2025-04-10 09:46:27.94788	pending
71	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:48:55.982399	2025-04-10 09:48:55.982402	pending
72	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:48:56.332264	2025-04-10 09:48:56.332271	pending
73	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:48:56.553285	2025-04-10 09:48:56.553292	pending
74	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:52:05.517654	2025-04-10 09:52:05.517658	pending
75	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:52:05.763358	2025-04-10 09:52:05.763361	pending
76	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:52:06.014941	2025-04-10 09:52:06.014943	pending
77	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:54:26.666794	2025-04-10 09:54:26.666802	pending
78	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:54:26.861734	2025-04-10 09:54:26.861736	pending
79	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:54:27.080781	2025-04-10 09:54:27.080786	pending
80	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:56:15.24474	2025-04-10 09:56:15.244745	pending
81	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:56:15.552639	2025-04-10 09:56:15.552649	pending
82	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:56:15.738913	2025-04-10 09:56:15.738915	pending
83	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 10:59:03.116263	2025-04-10 09:59:03.116267	pending
84	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 10:59:03.324123	2025-04-10 09:59:03.324127	pending
85	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 10:59:03.536202	2025-04-10 09:59:03.536205	pending
86	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 11:00:49.049387	2025-04-10 10:00:49.04939	pending
87	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 11:00:49.24458	2025-04-10 10:00:49.244585	pending
88	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 11:00:49.723231	2025-04-10 10:00:49.723246	pending
89	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 11:02:14.861566	2025-04-10 10:02:14.861569	pending
90	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 11:02:15.071645	2025-04-10 10:02:15.071651	pending
91	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 11:02:15.266093	2025-04-10 10:02:15.266095	pending
95	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 11:55:30.383041	2025-04-10 10:55:30.383045	pending
96	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 11:55:30.583485	2025-04-10 10:55:30.583493	pending
97	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 11:55:30.762201	2025-04-10 10:55:30.762203	pending
98	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 11:59:15.054003	2025-04-10 10:59:15.054006	pending
99	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 11:59:15.230892	2025-04-10 10:59:15.230895	pending
100	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 11:59:15.474168	2025-04-10 10:59:15.474173	pending
101	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:00:23.927981	2025-04-10 11:00:23.927986	pending
102	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:00:24.12134	2025-04-10 11:00:24.121349	pending
103	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:00:24.497899	2025-04-10 11:00:24.497903	pending
104	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:00:35.470606	2025-04-10 11:00:35.47061	pending
105	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:00:35.974333	2025-04-10 11:00:35.974338	pending
106	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:00:36.160771	2025-04-10 11:00:36.160776	pending
107	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:00:46.960858	2025-04-10 11:00:46.960861	pending
108	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:00:47.16963	2025-04-10 11:00:47.169636	pending
109	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:00:47.373727	2025-04-10 11:00:47.373733	pending
110	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:02:24.626646	2025-04-10 11:02:24.626651	pending
111	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:02:24.817271	2025-04-10 11:02:24.817279	pending
112	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:02:25.044722	2025-04-10 11:02:25.044729	pending
113	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:04:00.434807	2025-04-10 11:04:00.43481	pending
114	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:04:00.616608	2025-04-10 11:04:00.616613	pending
115	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:04:00.804822	2025-04-10 11:04:00.804825	pending
116	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:06:07.714619	2025-04-10 11:06:07.714623	pending
117	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:06:08.164068	2025-04-10 11:06:08.164071	pending
118	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:06:08.360558	2025-04-10 11:06:08.360562	pending
119	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:07:26.508174	2025-04-10 11:07:26.508179	pending
120	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:07:26.714129	2025-04-10 11:07:26.714133	pending
121	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:07:26.904503	2025-04-10 11:07:26.904505	pending
122	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:08:48.053371	2025-04-10 11:08:48.053374	pending
123	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:08:48.245993	2025-04-10 11:08:48.245996	pending
124	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:08:48.510079	2025-04-10 11:08:48.510081	pending
125	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:11:53.953117	2025-04-10 11:11:53.95312	pending
126	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:11:54.136251	2025-04-10 11:11:54.136255	pending
127	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:11:54.338931	2025-04-10 11:11:54.338937	pending
128	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:13:01.995008	2025-04-10 11:13:01.995012	pending
129	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:13:02.737384	2025-04-10 11:13:02.737388	pending
130	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:13:02.935624	2025-04-10 11:13:02.935631	pending
131	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:13:16.467404	2025-04-10 11:13:16.467408	pending
132	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:13:16.662982	2025-04-10 11:13:16.662989	pending
133	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:13:16.851354	2025-04-10 11:13:16.851358	pending
134	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:13:26.605145	2025-04-10 11:13:26.60515	pending
135	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:13:27.039051	2025-04-10 11:13:27.039064	pending
136	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:13:27.228765	2025-04-10 11:13:27.22877	pending
137	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:36:59.602774	2025-04-10 11:36:59.602792	pending
138	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:36:59.832079	2025-04-10 11:36:59.832083	pending
139	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:37:00.536184	2025-04-10 11:37:00.536189	pending
140	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:40:46.982763	2025-04-10 11:40:46.982767	pending
141	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:40:47.176123	2025-04-10 11:40:47.176125	pending
142	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:40:48.380145	2025-04-10 11:40:48.380148	pending
143	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 12:42:38.172163	2025-04-10 11:42:38.172167	pending
144	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 12:42:38.357199	2025-04-10 11:42:38.357202	pending
145	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 12:42:38.538594	2025-04-10 11:42:38.5386	pending
146	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:09.143261	2025-04-10 12:27:09.143267	pending
147	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:09.327985	2025-04-10 12:27:09.327988	pending
148	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:09.526087	2025-04-10 12:27:09.526091	pending
149	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:11.626685	2025-04-10 12:27:11.626689	pending
150	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:13.009564	2025-04-10 12:27:13.009568	pending
151	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:13.193685	2025-04-10 12:27:13.193688	pending
152	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:13.525648	2025-04-10 12:27:13.52565	pending
153	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:14.108711	2025-04-10 12:27:14.108723	pending
154	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:14.42232	2025-04-10 12:27:14.422326	pending
155	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:14.483728	2025-04-10 12:27:14.483734	pending
156	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:15.865988	2025-04-10 12:27:15.86599	pending
157	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:16.07142	2025-04-10 12:27:16.071423	pending
158	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:16.300793	2025-04-10 12:27:16.300795	pending
159	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:16.39509	2025-04-10 12:27:16.395093	pending
160	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:16.461836	2025-04-10 12:27:16.461838	pending
161	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:16.815002	2025-04-10 12:27:16.815008	pending
162	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:19.856269	2025-04-10 12:27:19.856273	pending
163	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:20.056212	2025-04-10 12:27:20.056216	pending
164	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:20.26602	2025-04-10 12:27:20.266023	pending
165	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:27:21.992407	2025-04-10 12:27:21.992418	pending
166	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:27:22.195641	2025-04-10 12:27:22.195645	pending
167	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:27:22.371249	2025-04-10 12:27:22.371253	pending
168	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:30:02.309664	2025-04-10 12:30:02.309668	pending
169	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:30:02.499594	2025-04-10 12:30:02.499597	pending
170	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:30:02.678215	2025-04-10 12:30:02.678221	pending
171	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:30:12.921563	2025-04-10 12:30:12.921564	pending
172	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:30:13.086116	2025-04-10 12:30:13.08612	pending
173	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:30:13.281892	2025-04-10 12:30:13.281896	pending
174	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:34:03.587919	2025-04-10 12:34:03.587928	pending
175	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:34:03.816375	2025-04-10 12:34:03.816379	pending
176	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:34:03.995047	2025-04-10 12:34:03.99505	pending
177	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:34:49.185773	2025-04-10 12:34:49.185777	pending
178	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:34:49.40575	2025-04-10 12:34:49.405752	pending
179	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:34:49.58488	2025-04-10 12:34:49.584884	pending
180	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:39:25.452849	2025-04-10 12:39:25.452855	pending
181	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:39:25.651043	2025-04-10 12:39:25.651047	pending
182	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:39:25.861942	2025-04-10 12:39:25.861947	pending
183	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:41:21.283025	2025-04-10 12:41:21.283029	pending
184	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:41:21.468662	2025-04-10 12:41:21.468668	pending
185	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:41:21.656314	2025-04-10 12:41:21.656319	pending
186	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:47:07.00123	2025-04-10 12:47:07.001235	pending
187	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:47:07.558401	2025-04-10 12:47:07.558406	pending
188	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:47:07.805839	2025-04-10 12:47:07.805845	pending
189	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:52:46.398296	2025-04-10 12:52:46.398298	pending
190	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:52:46.576706	2025-04-10 12:52:46.576708	pending
191	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:52:47.028893	2025-04-10 12:52:47.0289	pending
192	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 13:57:42.912763	2025-04-10 12:57:42.912767	pending
193	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 13:57:43.354497	2025-04-10 12:57:43.354501	pending
194	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 13:57:43.542824	2025-04-10 12:57:43.542827	pending
195	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 14:07:58.43693	2025-04-10 13:07:58.436934	pending
196	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 14:07:58.624639	2025-04-10 13:07:58.624645	pending
197	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 14:07:58.83214	2025-04-10 13:07:58.832145	pending
198	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 14:32:45.913353	2025-04-10 13:32:45.913356	pending
199	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 14:32:46.110633	2025-04-10 13:32:46.110637	pending
200	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 14:32:47.309451	2025-04-10 13:32:47.309455	pending
201	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 14:32:50.279195	2025-04-10 13:32:50.279201	pending
202	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 14:32:50.476805	2025-04-10 13:32:50.476812	pending
203	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 14:34:37.170055	2025-04-10 13:34:37.170059	pending
204	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 14:34:37.375791	2025-04-10 13:34:37.375803	pending
205	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 14:34:37.567983	2025-04-10 13:34:37.567989	pending
206	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 14:44:57.136599	2025-04-10 13:44:57.136604	pending
207	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 14:44:57.330167	2025-04-10 13:44:57.330171	pending
208	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 14:44:57.551231	2025-04-10 13:44:57.551234	pending
209	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 15:27:00.704138	2025-04-10 14:27:00.704142	pending
210	2	52	Item 'Corneto Chocolate' has expired	expiry	high	f	2025-04-10 15:27:00.948498	2025-04-10 14:27:00.948502	pending
211	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 15:27:01.152752	2025-04-10 14:27:01.152766	pending
212	2	47	Item 'Smirnoff (1L)' has expired	expiry	high	f	2025-04-10 15:27:56.84903	2025-04-10 14:27:56.849033	pending
213	2	84	Item 'Dairy milk' has expired	expiry	high	f	2025-04-10 15:27:57.355043	2025-04-10 14:27:57.355049	pending
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: divyanshsingh
--

COPY public.reports (user_id, date, total_items, total_value, expiring_items, expired_items, low_stock_items, total_sales, total_purchases, report_data, is_public, public_token, id, created_at, updated_at) FROM stdin;
2	2025-04-08	6	0	3	0	3	0	0	{"summary": {"total_items": 6, "expiring_items": 3, "expired_items": 0, "low_stock_items": 3, "critical_items": 1, "high_value_expiring": 0}, "expiry_analysis": {"next_week": {"count": 3, "items": [{"id": 48, "name": "Doritos", "quantity": 4.0, "unit": "box", "expiry_date": "2025-04-09", "days_until_expiry": 1, "location": null, "batch_number": null, "value": 14.0}, {"id": 32, "name": "Monster Energy Drinks", "quantity": 150.0, "unit": "pcs", "expiry_date": "2025-04-12", "days_until_expiry": 4, "location": null, "batch_number": null, "value": 675.0}, {"id": 47, "name": "Smirnoff (1L)", "quantity": 3.0, "unit": "box", "expiry_date": "2025-04-10", "days_until_expiry": 2, "location": null, "batch_number": null, "value": 29.97}]}, "next_month": {"count": 0, "items": []}, "next_quarter": {"count": 1, "items": [{"id": 51, "name": "Cheetos", "quantity": 3.0, "unit": "box", "expiry_date": "2025-06-27", "days_until_expiry": 80, "location": null, "batch_number": null, "value": 4.5}]}}, "risk_analysis": {"critical_items": [{"id": 32, "name": "Monster Energy Drinks", "quantity": 150.0, "unit": "pcs", "expiry_date": "2025-04-12", "days_until_expiry": 4, "location": null, "batch_number": null, "value": 675.0}], "high_value_expiring": []}, "historical_comparison": {"last_week": null}, "action_recommendations": [{"type": "urgent", "message": "Take immediate action on 3 items expiring in the next week", "item_ids": [48, 32, 47]}, {"type": "high_priority", "message": "Review 1 critical items with high quantity and near expiry", "item_ids": [32]}, {"type": "value_protection", "message": "Consider discounting 0 high-value items approaching expiry", "item_ids": []}]}	f	wJtb0cqbZkhwd0fK5D2N-ASjrJr865yggWu5-mThERY	3	2025-04-08 15:58:01.601878	2025-04-08 15:58:01.601881
2	2025-04-09	6	0	3	2	2	0	0	{"summary": {"total_items": 6, "expiring_items": 3, "expired_items": 2, "low_stock_items": 2, "critical_items": 2, "high_value_expiring": 0}, "expiry_analysis": {"next_week": {"count": 2, "items": [{"id": 80, "name": "Bacon Sandwich", "quantity": 35.0, "unit": "pcs", "expiry_date": "2025-04-16", "days_until_expiry": 7, "location": null, "batch_number": null, "value": 87.5}, {"id": 47, "name": "Smirnoff (1L)", "quantity": 3.0, "unit": "box", "expiry_date": "2025-04-10", "days_until_expiry": 1, "location": null, "batch_number": null, "value": 29.97}]}, "next_month": {"count": 1, "items": [{"id": 82, "name": "CheeseCake", "quantity": 15.0, "unit": "pcs", "expiry_date": "2025-04-24", "days_until_expiry": 15, "location": null, "batch_number": null, "value": 150.0}]}, "next_quarter": {"count": 0, "items": []}}, "risk_analysis": {"critical_items": [{"id": 82, "name": "CheeseCake", "quantity": 15.0, "unit": "pcs", "expiry_date": "2025-04-24", "days_until_expiry": 15, "location": null, "batch_number": null, "value": 150.0}, {"id": 80, "name": "Bacon Sandwich", "quantity": 35.0, "unit": "pcs", "expiry_date": "2025-04-16", "days_until_expiry": 7, "location": null, "batch_number": null, "value": 87.5}], "high_value_expiring": []}, "historical_comparison": {"last_week": null}, "action_recommendations": [{"type": "urgent", "message": "Take immediate action on 2 items expiring in the next week", "item_ids": [80, 47]}, {"type": "high_priority", "message": "Review 2 critical items with high quantity and near expiry", "item_ids": [82, 80]}, {"type": "value_protection", "message": "Consider discounting 0 high-value items approaching expiry", "item_ids": []}]}	f	ghha-hpg-rY5q1cbos34OSKEflLK3glIM45JewiYRN8	4	2025-04-09 05:34:48.235321	2025-04-09 05:34:48.235326
2	2025-04-10	8	0	1	3	2	0	0	{"summary": {"total_items": 8, "expiring_items": 1, "expired_items": 3, "low_stock_items": 2, "critical_items": 1, "high_value_expiring": 0}, "expiry_analysis": {"next_week": {"count": 1, "items": [{"id": 80, "name": "Bacon Sandwich", "quantity": 35.0, "unit": "pcs", "expiry_date": "2025-04-16", "days_until_expiry": 6, "location": null, "batch_number": null, "value": 87.5}]}, "next_month": {"count": 0, "items": []}, "next_quarter": {"count": 2, "items": [{"id": 87, "name": "Alphenlibe", "quantity": 10.0, "unit": "box", "expiry_date": "2025-07-04", "days_until_expiry": 85, "location": null, "batch_number": null, "value": 0.0}, {"id": 82, "name": "CheeseCake", "quantity": 135.0, "unit": "pcs", "expiry_date": "2025-06-27", "days_until_expiry": 78, "location": null, "batch_number": null, "value": 337.5}]}}, "risk_analysis": {"critical_items": [{"id": 80, "name": "Bacon Sandwich", "quantity": 35.0, "unit": "pcs", "expiry_date": "2025-04-16", "days_until_expiry": 6, "location": null, "batch_number": null, "value": 87.5}], "high_value_expiring": []}, "historical_comparison": {"last_week": null}, "action_recommendations": [{"type": "urgent", "message": "Take immediate action on 1 items expiring in the next week", "item_ids": [80]}, {"type": "high_priority", "message": "Review 1 critical items with high quantity and near expiry", "item_ids": [80]}, {"type": "value_protection", "message": "Consider discounting 0 high-value items approaching expiry", "item_ids": []}]}	f	tk4fGFT1PgyI0ToKg5WpC7WQs8acDWlI-a8FnyYGJso	5	2025-04-10 12:57:27.733075	2025-04-10 12:57:27.733079
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: divyanshsingh
--

COPY public.users (id, username, email, password_hash, password_reset_token, is_active, is_admin, created_at, updated_at, last_login, notification_preferences, verification_code, verification_code_expires_at, is_verified, email_notifications, sms_notifications, in_app_notifications, zoho_client_id, zoho_client_secret, zoho_access_token, zoho_refresh_token, zoho_token_expires_at, zoho_organization_id, password_reset_token_expires_at, login_attempts, locked_until) FROM stdin;
14	Vedanshi	singhdivyansh919@gmail.com	$2b$12$ofyuEHUBjdhbK1Q.7EByqOTwyn9hf/LxRH7kfy5Anuo8Ac3qcsJSC	\N	t	f	2025-04-10 13:04:25.924562	2025-04-10 13:06:17.668994	2025-04-10 13:06:17.66888	{}	\N	\N	t	f	f	f	\N	\N	\N	\N	\N	\N	\N	0	\N
8	testuser	test@example.com	$2b$12$rtCJUYaV1w7U2FMA9B7AfuZ/lyBRaLIle.Adg/IB5oKKvP2QjpMMK	\N	t	f	2025-04-08 16:24:06.842655	2025-04-08 16:28:38.619638	\N	{}	\N	\N	f	f	f	t	\N	\N	\N	\N	\N	\N	\N	0	\N
2	Divyansh	divyanshsingh1800@gmail.com	$2b$12$0MPEfsEMhDRy50hQgevw2uqlfgrrTgNEj53U7foZVd0hse9uxpsk.	\N	t	f	2025-04-05 11:57:18.286835	2025-04-10 13:32:41.189228	2025-04-10 13:07:48.68841	{}	\N	\N	t	f	f	t	1000.AGBPL2P1XANKWPHHG46NH9F8F26AKX	2c02760a0e7d555158ced01534629ed55104bd2708	1000.88fc56f318d1e30e452058d0121fd710.44c3773cb0ab105b5bc29cb1dd2754ef	1000.01c010b465adacef009dfcd5374c247d.9ccb6fc14ec6d317709628f115e28582	2025-04-10 15:32:41.187653	20105064935	\N	0	\N
\.


--
-- Name: items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: divyanshsingh
--

SELECT pg_catalog.setval('public.items_id_seq', 88, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: divyanshsingh
--

SELECT pg_catalog.setval('public.notifications_id_seq', 213, true);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: divyanshsingh
--

SELECT pg_catalog.setval('public.reports_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: divyanshsingh
--

SELECT pg_catalog.setval('public.users_id_seq', 14, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: items items_zoho_item_id_key; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_zoho_item_id_key UNIQUE (zoho_item_id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: reports reports_date_key; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_date_key UNIQUE (date);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: reports reports_public_token_key; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_public_token_key UNIQUE (public_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: items items_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: reports reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: divyanshsingh
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

