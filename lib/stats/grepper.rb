# usage: ruby grepper.rb /fully/qualified/path/to/listfile[accts] /fully/qualified/path/to/.gz[sources] /fully/qualified/path/to/output/directory
require 'zlib'
require 'json'
require 'time'

# filter out tweets for list of users in their respective files

# but first, pre-process the annotated lists:
# crude: grep -w --ignore-case 'bot' 1k.csv | grep -vw --ignore-case 'human.*human' | awk -F"," '{print $1}' > bots.1k
# crude: grep -w --ignore-case 'human' 1k.csv | grep -vw --ignore-case 'bot.*bot' | awk -F"," '{print $1}' > humans.1k
# clean: awk -F',' '$10 ~ /Bot/ { print $1 }' 1k.all | awk -F'"' '{print $2}' > 1k.bots
# clean: awk -F',' '$10 ~ /Human/ { print $1 }' 1k.all | awk -F'"' '{print $2}' > 1k.humans

# or, pre-process (automated) simpleclassifier lists:
# awk -F',' '{ if( $2 == " bot" ) { print $3 } }' simpleclassifier.1k.csv > 1k.bots.raw
# sort -u 1k.bots.raw > 1k.bots
# remove leading whitespaces (added for readability) via vim: %s/ //g
# to only process a subset next time: awk 'FNR==NR {a[$0]++; next} !a[$0]' 1k.bots 1k.bots.new > 1k.bots.distinct
# after processing 1k.bots.distinct, cat the two files and sort -u, for next iteration

acct_list = []
File.open(ARGV[0], 'r') do |f|
  f.each_line do |line|
    acct_list.push("#{line.strip!}")
  end
end # auto file close
acct_list.uniq!
acct_list.sort!
#puts acct_list

pline = ""
out = ""
screen_name = ""

file_list = Dir.entries(ARGV[1])
file_list.delete(".") # remove . from the list
file_list.delete("..") # remove .. from the list
#file_list.sort!
#file_list.sort_by { |f| f.split("-")[2].to_i }
#puts file_list

file_list.each do |file|
  #puts ".. file: #{file} .."
  begin
    infile = open("#{ARGV[1]}/#{file}")
    gzi = Zlib::GzipReader.new(infile)
    gzi.each_line do |line|
      begin
        pline = JSON.parse(line)
        # check each line against the complete acct_list, instead of traversing over the whole .gz repeatedly
        if acct_list.include? pline['user']['screen_name']
          screen_name = "#{pline['user']['screen_name']}"
        elsif acct_list.include? pline['retweeted_status']['user']['screen_name']
          screen_name = "#{pline['retweeted_status']['user']['screen_name']}"
	elsif acct_list.include? pline['quoted_status']['user']['screen_name']
	  screen_name = "#{pline['quoted_status']['user']['screen_name']}"
	else
	  screen_name = ""
	end
	
	if screen_name != "" # write if not empty
	  #puts "found .. #{screen_name} .. writing to file .."
          File.open("#{ARGV[2]}/#{screen_name}", 'a') do |f|
	    f.puts(JSON.generate(pline))
	  end # auto file close
	end
      rescue
        next
      end
    end
  rescue => e
    puts e
  end
end

