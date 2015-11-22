/*
 * Copyright (c) 2013, CESNET. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 *   o Redistributions of source code must retain the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer.
 *   o Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials
 *     provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
 * TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * Author: Michal Prochazka <michalp@ics.muni.cz>
 *
 * Program of reading packet trace files recorded by pcap
 * (used by tshark and tcpdump) and dumping out some corresponding information
 * in a human-readable form.
 *
 * Program can also strip packet payloads, so the resulting pcap file will
 * contain only packet headers. Usefull for anonymization.
 *
 * Program is based on code from inst.eecs.berkeley.edu/~ee122/fa07/projects/p2files/packet_parser.c, thanks!
 * 
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

#include <netinet/in.h>
#include <netinet/ip.h>
#define __FAVOR_BSD
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <arpa/inet.h>

#include <pcap.h>

#define VERSION "0.0.1"

/* Some helper functions, which we define at the end of this file. */

/* Returns a string representation of a timestamp. */
const char *timestamp_string(struct timeval ts);

/* Report a problem with dumping the packet with the given timestamp. */
void problem_pkt(struct timeval ts, const char *reason);

/* Report the specific problem of a packet being too short. */
void too_short(struct timeval ts, const char *truncated_hdr);

/* dump_packet()
 *
 * This routine parses a packet, expecting Ethernet, IP, and UDP or TCP headers.
 * It extracts the TCP/UDP source and destination IPs and port numbers along with the 
 * packet length. 
 */
void dump_packet(struct pcap_pkthdr *header, const unsigned char *packet, pcap_dumper_t *dump_file, int strip_payload)
{
	struct ip *ip;
	struct udphdr *udp;
	struct tcphdr *tcp;
	unsigned int IP_header_length;
	struct timeval ts = header->ts;
	unsigned int capture_len = header->len;
	const unsigned char *packet_hdr = packet;
     
	/* For simplicity, we assume Ethernet encapsulation. */
	if (capture_len < sizeof(struct ether_header)) {
		/* We didn't even capture a full Ethernet header, so we
		 * can't analyze this any further.
		 */
		too_short(ts, "Ethernet header");
		return;
	}

	/* Skip over the Ethernet header. */
	packet += sizeof(struct ether_header);
	capture_len -= sizeof(struct ether_header);

	if (capture_len < sizeof(struct ip)) {
		/* Didn't capture a full IP header */
		too_short(ts, "IP header");
		return;
	}

	ip = (struct ip*) packet;
	IP_header_length = ip->ip_hl * 4;	/* ip_hl is in 4-byte words */

	if (capture_len < IP_header_length) { 
		/* didn't capture the full IP header including options */
		too_short(ts, "IP header with options");
		return;
	}

	/* Skip over the IP header to get to the UDP or TCP header. */
	packet += IP_header_length;
	capture_len -= IP_header_length;

	/* UDP */
	if (ip->ip_p == IPPROTO_UDP) {
		if (capture_len < sizeof(struct udphdr)) {
			too_short(ts, "UDP header");
		} else {
			udp = (struct udphdr*) packet;

			if (dump_file == NULL) {
				printf("%s ", timestamp_string(ts));
				printf("src_ip=%s ", inet_ntoa(ip->ip_src));
				printf("dst_ip=%s ", inet_ntoa(ip->ip_dst));
				printf("UDP src_port=%d dst_port=%d length=%d\n",
						ntohs(udp->uh_sport),
						ntohs(udp->uh_dport),
						ntohs(udp->uh_ulen));
			} else {
				if (strip_payload == 1) {
					// Strip payload by setting the caplen to the full header size without payload
					header->caplen=sizeof(struct ether_header)+IP_header_length+sizeof(struct udphdr);
					header->len=sizeof(struct ether_header)+IP_header_length+sizeof(struct udphdr);
				}

				// Dump to a file
				pcap_dump((u_char *) dump_file, header, packet_hdr) ;
			}
		}
	} else if (ip->ip_p == IPPROTO_TCP) {
		/* TCP */
		if (capture_len < sizeof(struct tcphdr)) {
			too_short(ts, "TCP header");
		} else {
			tcp = (struct tcphdr*) packet;
			int TCP_header_length = tcp->th_off*4;

			if (dump_file == NULL) {
				printf("%s ", timestamp_string(ts));
				printf("src_ip=%s ", inet_ntoa(ip->ip_src));
				printf("dst_ip=%s ", inet_ntoa(ip->ip_dst));
				printf("TCP src_port=%d dst_port=%d length=%d\n",
						ntohs(tcp->th_sport),
						ntohs(tcp->th_dport),
						capture_len-TCP_header_length);
			} else {
				if (strip_payload == 1) {
				  // Strip payload by setting the caplen to the full header size without payload, including 12 bytes for options
				  header->caplen=sizeof(struct ether_header)+IP_header_length+TCP_header_length;
				  header->len=sizeof(struct ether_header)+IP_header_length+TCP_header_length;
				}

				// Dump to a file
				pcap_dump((u_char *) dump_file, header, packet_hdr) ;
			}
		}
	}
}

void usage() {
	printf("PCAP filter %s, CESNET (c) 2012\n\nUsage: ./pcap_filter [-s] [-f \"filter\"] [-o dump_filename] -i input_file\n\n", VERSION);
	printf("\t-i input file, must be in format which can be read by pcap library, supports only ethernet encapsulation\n");
	printf("\t-s strip packet payload, leave only packet headers (Ethernet, IP, TCP/UDP)\n");
	printf("\t-o output file, will be written in PCAP format\n");
	printf("\t-f filter (similar to tcpdump filters)\n");
	exit(1);
}

int main(int argc, char *argv[])
{
	pcap_t *pcap;
	const unsigned char *packet;
	char errbuf[PCAP_ERRBUF_SIZE];
	struct pcap_pkthdr header;
	struct bpf_program prog; /* compiled bpf filter program */
	pcap_dumper_t *dump_file;
	int c;
	int strip_payload = 0;
	char *filter = NULL;
	char *dump_filename = NULL, *input_filename = NULL;

	opterr = 0;

	while ((c = getopt (argc, argv, "f:o:i:s")) != -1)
		switch (c)
		{
			case 's':
				strip_payload = 1;
				break;
			case 'f':
				filter = optarg;
				break;
			case 'o':
				dump_filename = optarg;
				break;
			case 'i':
				input_filename = optarg;
				break;
			case '?':
				if (optopt == 'f' || optopt == 'o' || optopt == 'i') {
					fprintf (stderr, "ERROR: Option -%c requires an argument.\n", optopt);
				} else if (isprint(optopt)) {
					fprintf (stderr, "ERROR: Unknown option `-%c'.\n", optopt);
				} else {
					fprintf (stderr, "ERROR: Unknown option character `\\x%x'.\n", optopt);
				}
				return 1;
			default:
				usage();
		}

	if (input_filename == NULL) {
	  fprintf (stderr, "ERROR: Parameter -i must be specified.\n\n");
	  usage();
	}

	pcap = pcap_open_offline(input_filename, errbuf);
	if (pcap == NULL) {
		fprintf(stderr, "ERROR: Error reading input file: %s\n", errbuf);
		exit(2);
	}


	if (filter != NULL) {	
		if (pcap_compile(pcap,&prog,filter,1,PCAP_NETMASK_UNKNOWN) < 0) {
			/*
			 * Print out appropriate text, followed by the error message
			 * generated by the packet capture library.
			 */
			fprintf(stderr, "ERROR: Error compiling filter: %s\n",
					pcap_geterr(pcap));
			exit(3);
		}

		if (pcap_setfilter(pcap, &prog) < 0) {
			/* Copy appropriate error text to prefix string, prestr */
			fprintf(stderr, "ERROR: Error installing filter: %s\n",
					pcap_geterr(pcap));
			exit(4);
		}
	}

	if (dump_filename != NULL) {
		dump_file = pcap_dump_open(pcap, dump_filename);	
		if(dump_file == NULL) {
			fprintf(stderr, "ERROR: Error opening output file: %s\n", pcap_geterr(pcap));
			exit(5);
		}
	}

	/* Now just loop through extracting packets as long as we have
	 * some to read.
	 */
	while ((packet = pcap_next(pcap, &header)) != NULL) {
		dump_packet(&header, packet, dump_file, strip_payload);
	}

	if (dump_file != NULL) {
		pcap_dump_close(dump_file);
	}

	// terminate
	return 0;
}


/* Note, this routine returns a pointer into a static buffer, and
 * so each call overwrites the value returned by the previous call.
 */
const char *timestamp_string(struct timeval ts) {
	static char timestamp_string_buf[256];

	sprintf(timestamp_string_buf, "%d.%06d",
			(int) ts.tv_sec, (int) ts.tv_usec);

	return timestamp_string_buf;
}

void problem_pkt(struct timeval ts, const char *reason) {
	fprintf(stderr, "ERROR: %s: %s\n", timestamp_string(ts), reason);
}

void too_short(struct timeval ts, const char *truncated_hdr) {
	fprintf(stderr, "ERROR: Packet with timestamp %s is truncated and lacks a full %s\n",
			timestamp_string(ts), truncated_hdr);
}
