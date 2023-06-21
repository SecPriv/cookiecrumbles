.PHONY: all clean run

CFLAGS=

all: run-flask

# stdbuf -o0 make run-flask
run-%: %.pp.pv
	@time proverif -lib webspi.pvl $(word 2,$(subst -, ,$@)).pp.pv \
	| sed "s/\(is true\)/\x1b[37;42m\1\x1b[0m/" | sed "s/\(cannot be proved\|is false\)/\x1b[37;41m\1\x1b[0m/" \
	| sed 's/\(event\|begin\|end\)\(([^ ]*)\)/\x1b[1;34m\1\2\x1b[0m/g'| sed 's/\(RESULT\|Query\)/\x1b[35;1m\1\x1b[0m/g' \
	| sed 's/\(attacker(.*\?)\)/\x1b[1;33m\1\x1b[0m/g' \
	| sed 's/\(mess(.*\?)\)/\x1b[1;38m\1\x1b[0m/g' | sed 's/\(table(.*\?)\)/\x1b[1;36m\1\x1b[0m/g'

%.pp.pv: %.pv application.inc.pv attacker.inc.pv user_agent.inc.pv
	cpp -P ${CFLAGS} -o $@ $<
	bat --theme=ansi --paging=never $@

clean:
	rm -f *.pp.pv
