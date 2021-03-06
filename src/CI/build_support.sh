#############  Global Functions  #############
if [ "${TERM-}" -a -z "${CI}" ]; then
    COLOR_RED=$(tput setaf 1)
    COLOR_GREEN=$(tput setaf 2)
    COLOR_BLUE=$(tput setaf 4)
    COLOR_ORANGE=$(tput setaf 3)
    COLOR_RESET=$(tput sgr0)
else
    COLOR_RED=""
    COLOR_GREEN=""
    COLOR_BLUE=""
    COLOR_ORANGE=""
    COLOR_RESET=""
fi

if [ -z "${QUIET}" ]; then
    status() {
        echo -e "${COLOR_BLUE}[${PRODUCT_NAME}] ${1}${COLOR_RESET}"
    }

    step() {
        echo -e "${COLOR_GREEN}  + ${1}${COLOR_RESET}"
    }

    info() {
        echo -e "${COLOR_ORANGE}  + ${1}${COLOR_RESET}"
    }

    error() {
        echo -e "${COLOR_RED}  + ${1}${COLOR_RESET}"
    }
else
    status() {
        :
    }

    step() {
        :
    }

    info() {
        :
    }

    error() {
        echo -e "${COLOR_RED}  + ${1}${COLOR_RESET}"
    }
fi

exists() {
  /usr/bin/command -v "$1" >/dev/null 2>&1
}

ensure_dir() {
    [ -n "${1}" ] && /bin/mkdir -p "${1}" && builtin cd "${1}"
}

cleanup() {
    :
}

caught_error() {
    error "ERROR during build step: ${1}"
    cleanup
    exit 1
}

