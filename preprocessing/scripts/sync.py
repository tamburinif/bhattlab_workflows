#!/usr/bin/env python
	"""
	(Re-)sync two filtered paired end FASTQ files.
	Given two filtered paired end read files and one of the original read files,
	re-sync the filtered reads by filtering out anything that is only present in
	one of the two files.

	Usage:
	  {command} <orig.fq> <reads_1.fq> <reads_2.fq> \\
	      <reads_1.synced.fq> <reads_2.synced.fq> <orphans.fq>

	The synced reads are written to disk as <reads_1.synced.fq> and
	<reads_2.synced.fq>. The orphans are put in orphans.fq.
	Afterwards some counts are printed.

	Both Illumina old-style and new-style paired-end header lines are supported
	and any (input or output) filename ending in .gz is assumed to be gzipped.
	The original read file is used to speed up processing: it contains all
	possible reads from both edited reads (in all files in the same order) so it
	can process all files line by line, not having to read a single file in
	memory. Some ideas were taken from [1].

	[1] https://gist.github.com/588841/

	Copyright (c) 2011 Leiden University Medical Center <humgen@lumc.nl>
	Copyright (c) 2011 Martijn Vermaat <m.vermaat.hg@lumc.nl>

	Modified on 7-6-17 by Joyce Kang
	"""


	import gzip
	import re
	import sys


	def sync_paired_end_reads(original, reads_a, reads_b, synced_a, synced_b, orphans):
	    """
	    Filter out reads from two paired end read files that are not present in
	    both of them. Do this in a reasonable amount of time by using a file
	    containing all of the reads for one of the paired ends.
	    All arguments are open file handles.
	    @arg original: File containing all original reads for one of the paired
	                   ends.
	    @arg reads_a:  First from paired end read files.
	    @arg reads_b:  Second from paired end read files.
	    @arg synced_a: Filtered reads from first paired end read file.
	    @arg synced_b: Filtered reads from second paired end read file.
	    @arg orphans:  Orphan reads (present in only one of the two files)
	    @return:       Quintuple (total_a, total_b, kept, orphaned_a, orphaned_b) containing counts
	                   of the number of reads read from both input files,
	                   the total number of reads kept in the synced results, and
	                   the total number of reads written to the orphans file.
	    @todo: Print warnings if obvious things are not right (a or b still has
	           lines after original is processed).
	    """

	    def next_record(fh):
	        return [fh.readline().strip() for i in range(4)]

	    def head(record):
	        full_head = record[0].split(' ')
	        return full_head[0]

	    headers = (x.strip().split(' ')[0] for i, x in enumerate(original) if not (i % 4))

	    total_a = total_b = kept = orphaned_a = orphaned_b = 0

	    a, b = next_record(reads_a), next_record(reads_b)

	    for header in headers:

	        if header == head(a) and header != head(b):
	            print('\n'.join(a), file=orphans)
	            a = next_record(reads_a)
	            orphaned_a += 1
	            total_a += 1

	        if header == head(b) and header != head(a):
	            print('\n'.join(b), file=orphans)
	            b = next_record(reads_b)
	            orphaned_b += 1
	            total_b += 1

	        if header == head(a) == head(b):
	            print('\n'.join(a), file=synced_a)
	            print('\n'.join(b), file=synced_b)
	            a, b = next_record(reads_a), next_record(reads_b)
	            kept += 1
	            total_a += 1
	            total_b += 1

	    return total_a, total_b, kept, orphaned_a, orphaned_b


	def _open(filename, mode='r'):
	    if filename.endswith('.gz'):
	        return gzip.open(filename, mode)
	    return open(filename, mode)


	if __name__ == '__main__':
	    if len(sys.argv) < 7:
	        sys.stderr.write(__doc__.split('\n\n\n')[0].strip().format(
	            command=sys.argv[0]) + '\n')
	        sys.exit(1)
	    try:
	        original = _open(sys.argv[1], 'rt')
	        reads_a = _open(sys.argv[2], 'rt')
	        reads_b = _open(sys.argv[3], 'rt')
	        synced_a = _open(sys.argv[4], 'w')
	        synced_b = _open(sys.argv[5], 'w')
	        orphans = _open(sys.argv[6], 'w')
	        total_a, total_b, kept, orphaned_a, orphaned_b = \
	                    sync_paired_end_reads(original, reads_a, reads_b,
	                                          synced_a, synced_b, orphans)
	        print('Total %i reads from forward read file.' % total_a)
	        print('Total %i reads from reverse read file.' % total_b)
	        print('Synced read files contain %i reads.' % kept)
	        print('Put %i forward reads in the orphans file.' % orphaned_a)
	        print('Put %i reverse reads in the orphans file.' % orphaned_b)
	    except IOError as xxx_todo_changeme:
	        (_, message) = xxx_todo_changeme.args
	        sys.stderr.write('Error: %s\n' % message)
	        sys.exit(1)
