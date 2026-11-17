/* Link against the pinned upstream matcher to check long desktop metadata. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <match.h>

int main(void) {
    const char *blender =
        "Blender/var/lib/snapd/desktop/applications/blender_blender.desktop"
        "/snap/bin/blender3D modeling, animation, rendering and post-production"
        "Graphics;3DGraphics;3dcgmodelinganimationpaintingsculptingtexturing"
        "video editingvideo trackingrenderingrender enginecyclespython3D modeler";
    const char *scattered = "b_x_l_x_e_x_n_x_d_x_e_x_r";
    assert(strlen(blender) == 274);
    assert(match_for_matching_mode("blender", blender, MATCHING_MODE_FUZZY, true));
    assert(match_for_matching_mode("blender", scattered, MATCHING_MODE_FUZZY, true));
    assert(sort_for_matching_mode(blender, scattered, 0,
                                 MATCHING_MODE_FUZZY, "blender", true) < 0);
    assert(sort_for_matching_mode(scattered, blender, 0,
                                 MATCHING_MODE_FUZZY, "blender", true) > 0);
    assert(match_for_matching_mode("bldr", blender, MATCHING_MODE_FUZZY, true));
    assert(!match_for_matching_mode("BLENDER", blender, MATCHING_MODE_FUZZY, false));

    /* A candidate at the new boundary must still receive a finite score. */
    char boundary[4097], over_limit[4098];
    memset(boundary, 'x', sizeof(boundary) - 1);
    memcpy(boundary, "Blender", 7);
    boundary[sizeof(boundary) - 1] = '\0';
    memcpy(over_limit, boundary, sizeof(boundary) - 1);
    over_limit[4096] = 'x';
    over_limit[4097] = '\0';
    assert(sort_for_matching_mode(boundary, over_limit, 0,
                                 MATCHING_MODE_FUZZY, "blender", true) < 0);
    puts("Wofi fuzzy ranking: Blender, abbreviations, case, and 4096-byte boundary passed");
    return 0;
}
