from clusters.trackball_orbyl import TrackballOrbyl
import json
import os


class TrackballWild(TrackballOrbyl):
    key_to_thumb_rotation = [] # may no longer be used?
    post_offsets = [
            [14, -8, 3],
            [3, -9, -7],
            [-4, 4, -6],
            [-5, 18, 19]
        ]

    @staticmethod
    def name():
        return "TRACKBALL_WILD"


    def get_config(self):
        with open(os.path.join(".", "clusters", "json", "TRACKBALL_WILD.json"), mode='r') as fid:
            data = json.load(fid)

        superdata = super().get_config()

        # overwrite any super variables with this class' needs
        for item in data:
            superdata[item] = data[item]

        for item in superdata:
            if not hasattr(self, str(item)):
                print(self.name() + ": NO MEMBER VARIABLE FOR " + str(item))
                continue
            setattr(self, str(item), superdata[item])

        return superdata

    def __init__(self, parent_locals):
        super().__init__(parent_locals)
        for item in parent_locals:
            globals()[item] = parent_locals[item]

    def position_rotation(self):
        rot = [10, -15, 5]
        pos = self.thumborigin()
        # Changes size based on key diameter around ball, shifting off of the top left cluster key.
        shift = [-.9*self.key_diameter/2+27-42, -.1*self.key_diameter/2+3-20, -5]
        for i in range(len(pos)):
            pos[i] = pos[i] + shift[i] + self.translation_offset[i]

        for i in range(len(rot)):
            rot[i] = rot[i] + self.rotation_offset[i]

        return pos, rot


    def tl_place(self, shape):
        shape = rotate(shape, [0, 0, 0])
        t_off = self.key_translation_offsets[0]
        shape = rotate(shape, self.key_rotation_offsets[0])
        shape = translate(shape, (t_off[0], t_off[1]+self.key_diameter/2, t_off[2]))
        shape = rotate(shape, [0, 0, -80])
        shape = self.track_place(shape)

        return shape

    def mr_place(self, shape):
        shape = rotate(shape, [0, 0, 0])
        shape = rotate(shape, self.key_rotation_offsets[1])
        t_off = self.key_translation_offsets[1]
        shape = translate(shape, (t_off[0], t_off[1]+self.key_diameter/2, t_off[2]))
        shape = rotate(shape, [0, 0, -150])
        shape = self.track_place(shape)

        return shape

    def br_place(self, shape):
        shape = rotate(shape, [0, 0, 180])
        shape = rotate(shape, self.key_rotation_offsets[2])
        t_off = self.key_translation_offsets[2]
        shape = translate(shape, (t_off[0], t_off[1]+self.key_diameter/2, t_off[2]))
        shape = rotate(shape, [0, 0, -195])
        shape = self.track_place(shape)

        return shape

    def bl_place(self, shape):
        debugprint('thumb_bl_place()')
        shape = rotate(shape, [0, 0, 180])
        shape = rotate(shape, self.key_rotation_offsets[3])
        t_off = self.key_translation_offsets[3]
        shape = translate(shape, (t_off[0], t_off[1]+self.key_diameter/2, t_off[2]))
        shape = rotate(shape, [0, 0, -240])
        shape = self.track_place(shape)

        return shape


    def thumb_connectors(self, side="right"):
        print('thumb_connectors()')
        hulls = []

        # bottom 2 to tb
        hulls.append(
            triangle_hulls(
                [
                    self.track_place(self.tb_post_l()),
                    self.bl_place(web_post_tl()),
                    self.track_place(self.tb_post_bl()),
                    self.bl_place(web_post_tr()),
                    self.br_place(web_post_tl()),
                    self.track_place(self.tb_post_bl()),
                    self.br_place(web_post_tr()),
                    self.track_place(self.tb_post_br()),
                    self.br_place(web_post_tr()),
                    self.track_place(self.tb_post_br()),
                    self.mr_place(web_post_br()),
                    self.track_place(self.tb_post_r()),
                    self.mr_place(web_post_bl()),
                    self.tl_place(web_post_br()),
                    self.track_place(self.tb_post_r()),
                    self.tl_place(web_post_bl()),
                    self.track_place(self.tb_post_tr()),
                    key_place(web_post_bl(), 0, cornerrow),
                    self.track_place(self.tb_post_tl()),
                ]
            )
        )

        # bottom left
        hulls.append(
            triangle_hulls(
                [
                    self.bl_place(web_post_tr()),
                    self.br_place(web_post_tl()),
                    self.bl_place(web_post_br()),
                    self.br_place(web_post_bl()),
                ]
            )
        )

        # bottom right
        hulls.append(
            triangle_hulls(
                [
                    self.br_place(web_post_tr()),
                    self.mr_place(web_post_br()),
                    self.br_place(web_post_br()),
                    self.mr_place(web_post_tr()),
                ]
            )
        )
        # top right
        hulls.append(
            triangle_hulls(
                [
                    self.mr_place(web_post_bl()),
                    self.tl_place(web_post_br()),
                    self.mr_place(web_post_tl()),
                    self.tl_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_tl(), 2, lastrow),
                    key_place(web_post_bl(), 2, cornerrow),
                    key_place(web_post_tr(), 2, lastrow),
                    key_place(web_post_br(), 2, cornerrow),
                    key_place(web_post_bl(), 3, cornerrow),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_tr(), 3, lastrow),
                    key_place(web_post_br(), 3, lastrow),
                    key_place(web_post_tr(), 3, lastrow),
                    key_place(web_post_bl(), 4, cornerrow),
                ]
            )
        )

        return union(hulls)

    # todo update walls for wild track, still identical to orbyl
    def walls(self, side="right"):
        print('thumb_walls()')
        # thumb, walls
        shape = wall_brace(
            self.mr_place, .5, 1, web_post_tr(),
            (lambda sh: key_place(sh, 3, lastrow)), 0, -1, web_post_bl(),
        )
        # BOTTOM FRONT BETWEEN MR AND BR
        shape = union([shape, wall_brace(
            self.mr_place, .5, 1, web_post_tr(),
            self.br_place, 0, -1, web_post_br(),
        )])
        # BOTTOM FRONT AT BR
        shape = union([shape, wall_brace(
            self.br_place, 0, -1, web_post_br(),
            self.br_place, 0, -1, web_post_bl(),
        )])
        # BOTTOM FRONT BETWEEN BR AND BL
        shape = union([shape, wall_brace(
            self.br_place, 0, -1, web_post_bl(),
            self.bl_place, 0, -1, web_post_br(),
        )])
        # BOTTOM FRONT AT BL
        shape = union([shape, wall_brace(
            self.bl_place, 0, -1, web_post_br(),
            self.bl_place, -1, -1, web_post_bl(),
        )])
        # TOP LEFT BEHIND TRACKBALL
        shape = union([shape, wall_brace(
            self.track_place, -1.5, 0, self.tb_post_tl(),
            (lambda sh: left_key_place(sh, lastrow - 1, -1, side=ball_side, low_corner=True)), -1, 0, web_post(),
        )])
        # LEFT OF TRACKBALL
        shape = union([shape, wall_brace(
            self.track_place, -2, 0, self.tb_post_tl(),
            self.track_place, -2, 0, self.tb_post_l(),
        )])
        shape = union([shape, wall_brace(
            self.track_place, -2, 0, self.tb_post_l(),
            self.bl_place, -1, 0, web_post_tl(),
        )])

        # BEFORE BTUS
        #
        # # LEFT OF TRACKBALL
        # shape = union([shape, wall_brace(
        #     self.track_place, -1.5, 0, self.tb_post_tl(),
        #     self.track_place, -1, 0, self.tb_post_l(),
        # )])
        # shape = union([shape, wall_brace(
        #     self.track_place, -1, 0, self.tb_post_l(),
        #     self.bl_place, -1, 0, web_post_tl(),
        # )])

        shape = union([shape, wall_brace(
            self.bl_place, -1, 0, web_post_tl(),
            self.bl_place, -1, -1, web_post_bl(),
        )])

        return shape

    def connection(self, side='right'):
        print('thumb_connection()')
        # clunky bit on the top left thumb connection  (normal connectors don't work well)
        hulls = []
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 0, cornerrow),
                    left_key_place(web_post(), lastrow - 1, -1, side=side, low_corner=True),                # left_key_place(translate(web_post(), wall_locate1(-1, 0)), cornerrow, -1, low_corner=True),
                    self.track_place(self.tb_post_tl()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 1, cornerrow),
                    self.tl_place(web_post_bl()),
                    key_place(web_post_br(), 1, cornerrow),
                    self.tl_place(web_post_tl()),
                    key_place(web_post_bl(), 2, cornerrow),
                    self.tl_place(web_post_tl()),
                    key_place(web_post_br(), 2, cornerrow),
                    self.tl_place(web_post_tr()),
                    key_place(web_post_tl(), 3, lastrow),
                    key_place(web_post_bl(), 3, lastrow),
                    self.tl_place(web_post_tr()),
                    key_place(web_post_bl(), 3, lastrow),
                    self.mr_place(web_post_tl()),
                    key_place(web_post_br(), 3, lastrow),
                    key_place(web_post_bl(), 4, lastrow),
                    self.mr_place(web_post_tl()),
                    translate(self.mr_place(web_post_tl()), [0, 0, -5]),
                    key_place(web_post_br(), 3, lastrow),

                    key_place(web_post_bl(), 4, lastrow),
                    key_place(web_post_tr(), 3, lastrow),
                    key_place(web_post_tl(), 4, lastrow),
                    key_place(web_post_bl(), 4, cornerrow),
                    key_place(web_post_tr(), 4, lastrow),
                    key_place(web_post_br(), 4, cornerrow),
                    key_place(web_post_bl(), 5, cornerrow),
                ]
            )
        )
        shape = union(hulls)
        return shape
