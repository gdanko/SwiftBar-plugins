#include <inttypes.h>
#include <mach/host_info.h>
#include <mach/mach_host.h>
#include <mach/machine.h>
#include <stdio.h>
#include <sys/kernel.h>
#include <sys/sysctl.h>

/*
    /Library/Developer/CommandLineTools/SDKs/MacOSX14.4.sdk/usr/include/mach/host_info.h
    /Library/Developer/CommandLineTools/SDKs/MacOSX14.4.sdk/usr/include/mach/mach_host.h
    /Library/Developer/CommandLineTools/SDKs/MacOSX14.4.sdk/usr/include/sys/kernel.h
    /Library/Developer/CommandLineTools/SDKs/MacOSX14.4.sdk/usr/include/sys/sysctl.h
*/

uint64_t get_uint64_t(char* metric) {
    uint64_t output = 0;
    size_t size = sizeof(output);
    sysctlbyname(metric, &output, &size, NULL, 0);
    return output;
}

int main() {
    uint64_t cpu_type = get_uint64_t("hw.cputype");
    printf("%" PRIu64 "\n", cpu_type);
    uint64_t cpu_sub_type = get_uint64_t("hw.cpusubtype");
    printf("%" PRIu64 "\n", cpu_sub_type);
    uint64_t cpu_family = get_uint64_t("hw.cpufamily");
    printf("%" PRIu64 "\n", cpu_family);
    uint64_t cpu_sub_family = get_uint64_t("hw.cpusubfamily");
    printf("%" PRIu64 "\n", cpu_sub_family);
}