import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
# ---------------------------------------------------------------------------
# W02 - 2011
# Bruno da Silva Godoy - 111392
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Carregador de texturas
# ---------------------------------------------------------------------------
def load_texture(filename):
    if not os.path.exists(filename):
        return 0
    try:
        textureSurface = pygame.image.load(filename).convert_alpha()
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        return texid
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# CLASSE F1Car
# ---------------------------------------------------------------------------
class F1Car:
    def __init__(self, tire_tex_id=0, petronas_tex_id=0, aabar_tex_id=0, mercedes_tex_id=0, seven_tex_id=0):
        self.position = [0, 0.02, 0]
        self.rotation = 0
        self.wheel_rotation = 0
        self.speed = 0
        self.drs_open = False

        self.tire_tex_id = tire_tex_id
        self.petronas_tex_id = petronas_tex_id
        self.aabar_tex_id = aabar_tex_id
        self.mercedes_tex_id = mercedes_tex_id
        self.seven_tex_id = seven_tex_id

        self.body_color = (0.75, 0.75, 0.75)

    def draw_box(self, width, height, depth):
        w, h, d = width / 2, height / 2, depth / 2
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1);
        glVertex3f(-w, -h, d);
        glVertex3f(w, -h, d);
        glVertex3f(w, h, d);
        glVertex3f(-w, h, d)
        glNormal3f(0, 0, -1);
        glVertex3f(-w, -h, -d);
        glVertex3f(-w, h, -d);
        glVertex3f(w, h, -d);
        glVertex3f(w, -h, -d)
        glNormal3f(0, 1, 0);
        glVertex3f(-w, h, -d);
        glVertex3f(-w, h, d);
        glVertex3f(w, h, d);
        glVertex3f(w, h, -d)
        glNormal3f(0, -1, 0);
        glVertex3f(-w, -h, -d);
        glVertex3f(w, -h, -d);
        glVertex3f(w, -h, d);
        glVertex3f(-w, -h, d)
        glNormal3f(1, 0, 0);
        glVertex3f(w, -h, -d);
        glVertex3f(w, h, -d);
        glVertex3f(w, h, d);
        glVertex3f(w, -h, d)
        glNormal3f(-1, 0, 0);
        glVertex3f(-w, -h, -d);
        glVertex3f(-w, -h, d);
        glVertex3f(-w, h, d);
        glVertex3f(-w, h, -d)
        glEnd()

    def draw_line(self, p1, p2, thickness=2):
        glLineWidth(thickness)
        glBegin(GL_LINES)
        glVertex3f(*p1);
        glVertex3f(*p2)
        glEnd()

    def draw_manual_sphere(self, radius):
        lats, longs = 12, 12
        for i in range(lats):
            lat0 = math.pi * (-0.5 + float(i) / lats)
            z0 = radius * math.sin(lat0);
            zr0 = radius * math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / lats)
            z1 = radius * math.sin(lat1);
            zr1 = radius * math.cos(lat1)
            glBegin(GL_QUAD_STRIP)
            for j in range(longs + 1):
                lng = 2 * math.pi * float(j) / longs
                x = math.cos(lng);
                y = math.sin(lng)
                glNormal3f(x * zr0, y * zr0, z0);
                glVertex3f(x * zr0, y * zr0, z0)
                glNormal3f(x * zr1, y * zr1, z1);
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def draw_detailed_wheel(self, x, y, z, is_front):
        tire_radius = 0.26;
        tire_width = 0.26 if is_front else 0.38
        rim_radius = 0.17;
        hub_radius = 0.06
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(self.wheel_rotation, 1, 0, 0);
        glRotatef(90, 0, 1, 0)
        glTranslatef(0, 0, -tire_width / 2)
        quad = gluNewQuadric();
        gluQuadricNormals(quad, GLU_SMOOTH);
        gluQuadricTexture(quad, GL_TRUE)

        # Pneu
        glColor3f(0.15, 0.15, 0.15);
        gluCylinder(quad, tire_radius, tire_radius, tire_width, 30, 1)

        # Parte Interna
        glPushMatrix()
        glRotatef(180, 0, 1, 0)

        # Disco da roda
        glColor3f(0.25, 0.25, 0.28);
        gluDisk(quad, 0, tire_radius, 30, 1)

        # Parafusos
        glColor3f(0.7, 0.7, 0.75);
        bolt_radius = 0.015;
        bolt_dist = hub_radius + 0.05
        for i in range(5):
            glPushMatrix()
            angle = (360 / 5) * i;
            glRotatef(angle, 0, 0, 1)
            glTranslatef(bolt_dist, 0, 0);
            gluCylinder(quad, bolt_radius, bolt_radius, 0.02, 6, 1)
            glTranslatef(0, 0, 0.02);
            gluDisk(quad, 0, bolt_radius, 6, 1);
            glPopMatrix()

        # Cubo central
        glColor3f(0.15, 0.15, 0.18);
        gluCylinder(quad, hub_radius + 0.02, hub_radius + 0.02, 0.04, 20, 1)
        glTranslatef(0, 0, 0.04)
        glColor3f(0.3, 0.3, 0.35);
        gluDisk(quad, 0, hub_radius + 0.02, 20, 1)

        glPopMatrix()

        # Parede externa
        glPushMatrix()
        glTranslatef(0, 0, tire_width)
        glColor3f(0.15, 0.15, 0.15);
        gluDisk(quad, rim_radius, tire_radius, 30, 1)
        if self.tire_tex_id > 0:
            glEnable(GL_TEXTURE_2D);
            glBindTexture(GL_TEXTURE_2D, self.tire_tex_id)
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor3f(1.0, 1.0, 1.0);
            tex_w, tex_h = 0.10, 0.03;
            pos_radius = tire_radius - 0.05
            glPushMatrix();
            glTranslatef(0, pos_radius, 0.002);
            glNormal3f(0, 0, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0);
            glVertex3f(-tex_w, -tex_h, 0);
            glTexCoord2f(1.0, 1.0);
            glVertex3f(tex_w, -tex_h, 0)
            glTexCoord2f(1.0, 0.0);
            glVertex3f(tex_w, tex_h, 0);
            glTexCoord2f(0.0, 0.0);
            glVertex3f(-tex_w, tex_h, 0)
            glEnd();
            glPopMatrix()
            glPushMatrix();
            glRotatef(180, 0, 0, 1);
            glTranslatef(0, pos_radius, 0.002);
            glNormal3f(0, 0, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0);
            glVertex3f(-tex_w, -tex_h, 0);
            glTexCoord2f(1.0, 1.0);
            glVertex3f(tex_w, -tex_h, 0)
            glTexCoord2f(1.0, 0.0);
            glVertex3f(tex_w, tex_h, 0);
            glTexCoord2f(0.0, 0.0);
            glVertex3f(-tex_w, tex_h, 0)
            glEnd();
            glPopMatrix()
            glDisable(GL_BLEND);
            glDisable(GL_TEXTURE_2D)
        else:
            glPushMatrix();
            glTranslatef(0, 0, 0.002);
            glColor3f(1.0, 0.9, 0.0)
            gluPartialDisk(quad, tire_radius - 0.06, tire_radius - 0.02, 30, 1, 60, 60)
            gluPartialDisk(quad, tire_radius - 0.06, tire_radius - 0.02, 30, 1, 240, 60)
            glPopMatrix()
        glPopMatrix()

        # Cubo Externo
        glPushMatrix();
        glTranslatef(0, 0, tire_width - 0.03);
        glColor3f(0.6, 0.6, 0.65);
        gluDisk(quad, rim_radius - 0.03, rim_radius, 30, 1);
        glTranslatef(0, 0, -0.05);
        glColor3f(0.5, 0.5, 0.55);
        gluDisk(quad, hub_radius, rim_radius - 0.02, 30, 1);
        gluCylinder(quad, hub_radius, rim_radius - 0.03, 0.05, 30, 1);
        glPopMatrix()
        glPushMatrix();
        glTranslatef(0, 0, tire_width - 0.06);
        glColor3f(0.2, 0.15, 0.1);
        gluCylinder(quad, hub_radius, hub_radius, 0.04, 20, 1);
        glTranslatef(0, 0, 0.04);
        gluDisk(quad, 0.03, 0.06, 20, 1);
        glColor3f(0.9, 0.1, 0.4);
        gluCylinder(quad, 0.03, 0.015, 0.03, 15, 1);
        glTranslatef(0, 0, 0.03);
        gluDisk(quad, 0, 0.015, 15, 1);
        glPopMatrix()
        gluDeleteQuadric(quad);
        glPopMatrix()

    def draw_cockpit_base(self):
        glColor3f(*self.body_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0);
        glVertex3f(-0.10, 0.30, -0.7);
        glVertex3f(0.10, 0.30, -0.7);
        glVertex3f(0.18, 0.35, 0.9);
        glVertex3f(-0.18, 0.35, 0.9)
        glNormal3f(0, -1, 0);
        glVertex3f(-0.10, 0.125, -0.7);
        glVertex3f(0.10, 0.125, -0.7);
        glVertex3f(0.18, 0.125, 0.9);
        glVertex3f(-0.18, 0.125, 0.9)
        glNormal3f(1, 0, 0);
        glVertex3f(0.10, 0.30, -0.7);
        glVertex3f(0.10, 0.125, -0.7);
        glVertex3f(0.18, 0.125, 0.9);
        glVertex3f(0.18, 0.35, 0.9)
        glNormal3f(-1, 0, 0);
        glVertex3f(-0.10, 0.30, -0.7);
        glVertex3f(-0.10, 0.125, -0.7);
        glVertex3f(-0.18, 0.125, 0.9);
        glVertex3f(-0.18, 0.35, 0.9)
        glNormal3f(0, 0, -1);
        glVertex3f(-0.10, 0.30, -0.7);
        glVertex3f(0.10, 0.30, -0.7);
        glVertex3f(0.10, 0.125, -0.7);
        glVertex3f(-0.10, 0.125, -0.7)
        glEnd()

    def draw_curved_sidepod(self, side):
        z_f = 0.75;
        z_r = -0.8;
        xif = 0.18;
        xof = 0.52;
        xir = 0.05;
        xor = 0.35;
        yb = 0.125;
        yt = 0.35
        glBegin(GL_QUADS)
        # Topo
        glNormal3f(0, 1, 0);
        glColor3f(*self.body_color);
        glVertex3f(xif, yt, z_f);
        glVertex3f(xof, yt, z_f);
        glVertex3f(xor, yt - 0.1, z_r);
        glVertex3f(xir, yt - 0.05, z_r)
        # Lateral externa
        glNormal3f(1, 0, 0);
        glColor3f(0.65, 0.65, 0.65);
        glVertex3f(xof, yt, z_f);
        glVertex3f(xof, yb, z_f);
        glVertex3f(xor, yb, z_r);
        glVertex3f(xor, yt - 0.1, z_r)
        # Fundo
        glNormal3f(0, -1, 0);
        glColor3f(0.4, 0.4, 0.4);
        glVertex3f(xif, yb, z_f);
        glVertex3f(xof, yb, z_f);
        glVertex3f(xor, yb, z_r);
        glVertex3f(xir, yb, z_r)
        # Lateral interna
        glNormal3f(-1, 0, 0);
        glColor3f(0.65, 0.65, 0.65);
        glVertex3f(xir, yt - 0.05, z_r);
        glVertex3f(xor, yt - 0.1, z_r);
        glVertex3f(xor, yb, z_r);
        glVertex3f(xir, yb, z_r)
        glEnd()

        # Extensão Inferior
        glColor3f(*self.body_color)
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0);
        glVertex3f(0.52, 0.125, 0.75);
        glVertex3f(0.52, 0.125, 0.75);
        glVertex3f(0.35, 0.125, -0.8);
        glVertex3f(0.35, 0.125, -0.8)
        glNormal3f(0, 0, 1);
        glVertex3f(0.18, 0.125, 0.75);
        glVertex3f(0.18, 0.125, 0.75);
        glVertex3f(0.52, 0.125, 0.75);
        glVertex3f(0.52, 0.125, 0.75)
        glEnd()

        # Faixa verde
        glColor3f(0.0, 0.6, 0.55)
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0);
        glVertex3f(0.47, 0.32, 0.25);
        glVertex3f(0.47, 0.13, 0.25);
        glVertex3f(0.38, 0.12, -0.65);
        glVertex3f(0.38, 0.26, -0.65)
        glEnd()

        # --- Logo Petronas
        if self.petronas_tex_id > 0:
            glEnable(GL_TEXTURE_2D);
            glBindTexture(GL_TEXTURE_2D, self.petronas_tex_id)
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor3f(1.0, 1.0, 1.0)

            glBegin(GL_QUADS)
            if side == 1:
                glNormal3f(-1, 0, 0)
                glTexCoord2f(1.0, 0.0);
                glVertex3f(0.405, 0.06, -0.4)
                glTexCoord2f(0.0, 0.0);
                glVertex3f(0.485, 0.06, 0.25)
                glTexCoord2f(0.0, 1.0);
                glVertex3f(0.485, 0.29, 0.25)
                glTexCoord2f(1.0, 1.0);
                glVertex3f(0.405, 0.29, -0.4)
            else:
                glNormal3f(1, 0, 0)
                glTexCoord2f(0.0, 0.0);
                glVertex3f(0.405, 0.06, -0.4)
                glTexCoord2f(1.0, 0.0);
                glVertex3f(0.485, 0.06, 0.25)
                glTexCoord2f(1.0, 1.0);
                glVertex3f(0.485, 0.29, 0.25)
                glTexCoord2f(0.0, 1.0);
                glVertex3f(0.405, 0.29, -0.4)
            glEnd()
            glDisable(GL_BLEND);
            glDisable(GL_TEXTURE_2D)

        # Fechamentos traseiros
        glColor3f(0.65, 0.65, 0.65);
        z_back = 0.74
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1);
        glVertex3f(0.18, 0.35, z_back);
        glVertex3f(0.52, 0.35, z_back);
        glVertex3f(0.52, 0.125, z_back);
        glVertex3f(0.18, 0.125, z_back)
        glEnd()
        glColor3f(0.05, 0.05, 0.05)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1);
        glVertex3f(0.22, 0.31, 0.751);
        glVertex3f(0.48, 0.31, 0.751);
        glVertex3f(0.48, 0.165, 0.751);
        glVertex3f(0.22, 0.165, 0.751)
        glEnd()

    def draw_tapered_body(self):
        glColor3f(*self.body_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0);
        glVertex3f(-0.12, 0.55, 0.05);
        glVertex3f(0.12, 0.55, 0.05);
        glVertex3f(0.02, 0.35, -1.25);
        glVertex3f(-0.02, 0.35, -1.25)
        glNormal3f(1, 0, 0);
        glVertex3f(0.12, 0.55, 0.05);
        glVertex3f(0.25, 0.275, 0.05);
        glVertex3f(0.08, 0.25, -1.25);
        glVertex3f(0.02, 0.35, -1.25)
        glNormal3f(1, -1, 0);
        glVertex3f(0.25, 0.275, 0.05);
        glVertex3f(0.25, 0.125, 0.05);
        glVertex3f(0.08, 0.20, -1.25);
        glVertex3f(0.08, 0.25, -1.25)
        glNormal3f(-1, 0, 0);
        glVertex3f(-0.12, 0.55, 0.05);
        glVertex3f(-0.25, 0.275, 0.05);
        glVertex3f(-0.08, 0.25, -1.25);
        glVertex3f(-0.02, 0.35, -1.25)
        glNormal3f(-1, -1, 0);
        glVertex3f(-0.25, 0.275, 0.05);
        glVertex3f(-0.25, 0.125, 0.05);
        glVertex3f(-0.08, 0.20, -1.25);
        glVertex3f(-0.08, 0.25, -1.25)
        glEnd()


        # Extensão Inferior
        glColor3f(*self.body_color)
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0);
        glVertex3f(0.25, 0.125, 0.05);
        glVertex3f(0.25, 0.125, 0.05);
        glVertex3f(0.08, 0.125, -1.25);
        glVertex3f(0.08, 0.20, -1.25)
        glNormal3f(-1, 0, 0);
        glVertex3f(-0.25, 0.125, 0.05);
        glVertex3f(-0.08, 0.20, -1.25);
        glVertex3f(-0.08, 0.125, -1.25);
        glVertex3f(-0.25, 0.125, 0.05)
        glEnd()

        # Tampa Traseira
        glColor3f(*self.body_color)
        glBegin(GL_POLYGON)
        glNormal3f(0, 0, -1)
        glVertex3f(-0.02, 0.35, -1.25);
        glVertex3f(0.02, 0.35, -1.25);
        glVertex3f(0.08, 0.25, -1.25);
        glVertex3f(0.08, 0.20, -1.25)
        glVertex3f(0.08, 0.125, -1.25);
        glVertex3f(-0.08, 0.125, -1.25);
        glVertex3f(-0.08, 0.20, -1.25);
        glVertex3f(-0.08, 0.25, -1.25)
        glEnd()

    def draw_nose_w02(self):
        base_color = (0.75, 0.75, 0.78)
        glColor3f(*base_color)
        # Geometria do Bico
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0);
        glVertex3f(-0.18, 0.35, 0.9);
        glVertex3f(0.18, 0.35, 0.9);
        glVertex3f(0.06, 0.24, 1.6);
        glVertex3f(-0.06, 0.24, 1.6)
        glNormal3f(0, 1, 0);
        glVertex3f(-0.06, 0.24, 1.6);
        glVertex3f(0.06, 0.24, 1.6);
        glVertex3f(0.02, 0.18, 1.9);
        glVertex3f(-0.02, 0.18, 1.9)
        glNormal3f(1, 0, 0);
        glVertex3f(0.18, 0.35, 0.9);
        glVertex3f(0.18, 0.125, 0.9);
        glVertex3f(0.06, 0.14, 1.6);
        glVertex3f(0.06, 0.24, 1.6)
        glVertex3f(0.06, 0.24, 1.6);
        glVertex3f(0.06, 0.14, 1.6);
        glVertex3f(0.02, 0.16, 1.9);
        glVertex3f(0.02, 0.18, 1.9)
        glNormal3f(-1, 0, 0);
        glVertex3f(-0.18, 0.35, 0.9);
        glVertex3f(-0.18, 0.125, 0.9);
        glVertex3f(-0.06, 0.14, 1.6);
        glVertex3f(-0.06, 0.24, 1.6)
        glVertex3f(-0.06, 0.24, 1.6);
        glVertex3f(-0.06, 0.14, 1.6);
        glVertex3f(-0.02, 0.16, 1.9);
        glVertex3f(-0.02, 0.18, 1.9)
        glNormal3f(0, -1, 0);
        glVertex3f(-0.18, 0.125, 0.9);
        glVertex3f(0.18, 0.125, 0.9);
        glVertex3f(0.06, 0.14, 1.6);
        glVertex3f(-0.06, 0.14, 1.6)
        glVertex3f(-0.06, 0.14, 1.6);
        glVertex3f(0.06, 0.14, 1.6);
        glVertex3f(0.02, 0.16, 1.9);
        glVertex3f(-0.02, 0.16, 1.9)
        glNormal3f(0, 0, 1);
        glVertex3f(-0.02, 0.18, 1.9);
        glVertex3f(0.02, 0.18, 1.9);
        glVertex3f(0.02, 0.16, 1.9);
        glVertex3f(-0.02, 0.16, 1.9)
        glEnd()

        # Número 7 no Bico
        if self.seven_tex_id > 0:
            glEnable(GL_TEXTURE_2D);
            glBindTexture(GL_TEXTURE_2D, self.seven_tex_id)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glNormal3f(0, 1, 0)
            glTexCoord2f(0.0, 1.0);
            glVertex3f(-0.04, 0.275, 1.41)
            glTexCoord2f(1.0, 1.0);
            glVertex3f(0.04, 0.275, 1.41)
            glTexCoord2f(1.0, 0.0);
            glVertex3f(0.04, 0.265, 1.49)
            glTexCoord2f(0.0, 0.0);
            glVertex3f(-0.04, 0.265, 1.49)
            glEnd()
            glDisable(GL_BLEND);
            glDisable(GL_TEXTURE_2D)
            glColor3f(*base_color)

        # Adesivo Mercedes
        if self.mercedes_tex_id > 0:
            glEnable(GL_TEXTURE_2D);
            glBindTexture(GL_TEXTURE_2D, self.mercedes_tex_id)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glNormal3f(0, 1, 0)
            glTexCoord2f(0.0, 1.0);
            glVertex3f(-0.035, 0.225, 1.715)
            glTexCoord2f(1.0, 1.0);
            glVertex3f(0.035, 0.225, 1.715)
            glTexCoord2f(1.0, 0.0);
            glVertex3f(0.035, 0.205, 1.785)
            glTexCoord2f(0.0, 0.0);
            glVertex3f(-0.035, 0.205, 1.785)
            glEnd()
            glDisable(GL_BLEND);
            glDisable(GL_TEXTURE_2D)
            glColor3f(*base_color)

        # Câmeras
        glColor3f(0.1, 0.1, 0.1)
        for x_pos in [-0.05, 0.05]:
            glPushMatrix()
            glTranslatef(x_pos, 0.08, 1.65)
            glScalef(0.04, 0.25, 0.15)
            self.draw_box(1, 1, 1)
            glPopMatrix()

    def draw_gap_filler(self):
        glColor3f(*self.body_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, -0.4);
        glVertex3f(-0.07, 0.54, 0.025);
        glVertex3f(0.07, 0.54, 0.025);
        glVertex3f(0.12, 0.55, 0.05);
        glVertex3f(-0.12, 0.55, 0.05)
        glNormal3f(1, 0.3, -0.2);
        glVertex3f(0.07, 0.54, 0.025);
        glVertex3f(0.07, 0.36, 0.025);
        glVertex3f(0.25, 0.275, 0.05);
        glVertex3f(0.12, 0.55, 0.05)
        glNormal3f(-1, 0.3, -0.2);
        glVertex3f(-0.07, 0.54, 0.025);
        glVertex3f(-0.12, 0.55, 0.05);
        glVertex3f(-0.25, 0.275, 0.05);
        glVertex3f(-0.07, 0.36, 0.025)
        glEnd()

    def draw_suspension(self):
        glColor3f(0.15, 0.15, 0.15)
        # Dianteira
        self.draw_line((0.17, 0.34, 0.9), (0.80, 0.29, 1.1), 3)
        self.draw_line((0.12, 0.29, 1.3), (0.80, 0.29, 1.1), 3)
        self.draw_line((0.17, 0.11, 0.9), (0.80, 0.19, 1.1), 3)
        self.draw_line((0.12, 0.14, 1.3), (0.80, 0.19, 1.1), 3)
        self.draw_line((0.15, 0.32, 1.1), (0.80, 0.29, 1.1), 4)
        # Traseira
        self.draw_line((0.18, 0.42, -0.4), (0.80, 0.29, -1.0), 3)
        self.draw_line((0.08, 0.35, -1.1), (0.80, 0.29, -1.0), 3)
        self.draw_line((0.20, 0.12, -0.2), (0.80, 0.19, -1.0), 3)
        self.draw_line((0.08, 0.18, -1.1), (0.80, 0.19, -1.0), 3)
        self.draw_line((0.13, 0.38, -0.80), (0.80, 0.29, -1.0), 4)

    def draw_rear_wing_structure(self):
        wing_z = -1.25
        # Pilar e suportes
        glColor3f(0.15, 0.15, 0.15);
        glPushMatrix();
        glTranslatef(0, 0.5, wing_z + 0.05);
        glScalef(0.03, 0.6, 0.15);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glColor3f(0.3, 0.3, 0.3);
        glPushMatrix();
        glTranslatef(0, 0.78, wing_z + 0.08);
        glScalef(0.06, 0.04, 0.1);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        # Placa principal e DRS
        glColor3f(*self.body_color);
        glPushMatrix();
        glTranslatef(0, 0.65, wing_z);
        glScalef(0.72, 0.04, 0.25);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glPushMatrix();
        glTranslatef(0, 0.78, wing_z + 0.05);
        glRotatef(80 if self.drs_open else 0, 1, 0, 0);
        glScalef(0.68, 0.03, 0.12);
        self.draw_box(1, 1, 1);
        glPopMatrix()

        # Endplates Laterais
        for side in [-1, 1]:
            x_pos = side * 0.37
            glPushMatrix()
            glTranslatef(x_pos, 0.6, wing_z)
            # Base cinza
            glColor3f(*self.body_color);
            glPushMatrix();
            glScalef(0.02, 0.50, 0.4);
            self.draw_box(1, 1, 1);
            glPopMatrix()

            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor3f(1, 1, 1)

            # Adesivo Aabar
            if self.aabar_tex_id > 0:
                glEnable(GL_TEXTURE_2D);
                glBindTexture(GL_TEXTURE_2D, self.aabar_tex_id)
                glBegin(GL_QUADS)
                if side == 1:
                    glNormal3f(1, 0, 0);
                    glTexCoord2f(0, 0);
                    glVertex3f(0.011, -0.075, 0.16);
                    glTexCoord2f(1, 0);
                    glVertex3f(0.011, -0.075, -0.16);
                    glTexCoord2f(1, 1);
                    glVertex3f(0.011, 0.075, -0.16);
                    glTexCoord2f(0, 1);
                    glVertex3f(0.011, 0.075, 0.16)
                else:
                    glNormal3f(-1, 0, 0);
                    glTexCoord2f(1, 0);
                    glVertex3f(-0.011, -0.075, 0.16)
                    glTexCoord2f(0, 0);
                    glVertex3f(-0.011, -0.075, -0.16)
                    glTexCoord2f(0, 1);
                    glVertex3f(-0.011, 0.075, -0.16)
                    glTexCoord2f(1, 1);
                    glVertex3f(-0.011, 0.075, 0.16)
                glEnd()

            # Número 7 na Endplate
            if self.seven_tex_id > 0:
                glEnable(GL_TEXTURE_2D);
                glBindTexture(GL_TEXTURE_2D, self.seven_tex_id)
                glBegin(GL_QUADS)
                if side == 1:
                    glNormal3f(1, 0, 0);
                    glTexCoord2f(0, 0);
                    glVertex3f(0.011, -0.20, 0.08);
                    glTexCoord2f(1, 0);
                    glVertex3f(0.011, -0.20, -0.08);
                    glTexCoord2f(1, 1);
                    glVertex3f(0.011, -0.08, -0.08);
                    glTexCoord2f(0, 1);
                    glVertex3f(0.011, -0.08, 0.08)
                else:
                    glNormal3f(-1, 0, 0);
                    glTexCoord2f(1, 0);
                    glVertex3f(-0.011, -0.20, 0.08)
                    glTexCoord2f(0, 0);
                    glVertex3f(-0.011, -0.20, -0.08)
                    glTexCoord2f(0, 1);
                    glVertex3f(-0.011, -0.08, -0.08)
                    glTexCoord2f(1, 1);
                    glVertex3f(-0.011, -0.08, 0.08)
                glEnd()

            glDisable(GL_BLEND);
            glDisable(GL_TEXTURE_2D)
            glPopMatrix()

    def draw_driver(self):
        # --- Buraco do Cockpit
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0.33, 0.20)
        glRotatef(-4, 1, 0, 0)
        # Tamanho
        glScalef(0.24, 0.01, 0.55)
        self.draw_box(1, 1, 1)
        glPopMatrix()
        glColor3f(1.0, 0.85, 0.0);
        glPushMatrix();
        glTranslatef(0, 0.40, 0.3);
        self.draw_manual_sphere(0.13);
        glPopMatrix()

        # Viseira
        glColor3f(0.2, 0.2, 0.2);
        glPushMatrix();
        glTranslatef(0, 0.45, 0.35);
        glScalef(0.15, 0.07, 0.165);
        self.draw_box(1, 1, 1);
        glPopMatrix()

    def draw_new_mirrors(self):
        glColor3f(0.1, 0.1, 0.1);
        glPushMatrix();
        glTranslatef(0.22, 0.32, 0.75);
        glRotatef(45, 0, 0, 1);
        glScalef(0.25, 0.02, 0.02);
        glTranslatef(0.5, 0, 0);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glPushMatrix();
        glTranslatef(0.42, 0.50, 0.75);
        glRotatef(-10, 0, 1, 0)
        glColor3f(0.1, 0.1, 0.1);
        glPushMatrix();
        glScalef(0.12, 0.07, 0.08);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glColor3f(0.8, 0.8, 0.9);
        glPushMatrix();
        glTranslatef(0, 0, -0.041);
        glScalef(0.10, 0.05, 0.01);
        self.draw_box(1, 1, 1);
        glPopMatrix();
        glPopMatrix()

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation, 0, 1, 0)

        self.draw_cockpit_base()
        self.draw_driver()

        for sign in [1, -1]:
            glPushMatrix()
            glScalef(sign, 1, 1)
            self.draw_curved_sidepod(sign)
            self.draw_suspension()
            self.draw_new_mirrors()
            self.draw_detailed_wheel(0.88, 0.24, 1.1, True)
            self.draw_detailed_wheel(0.88, 0.24, -1.0, False)
            glPopMatrix()

        self.draw_tapered_body()
        self.draw_gap_filler()

        # Assoalho
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix();
        glTranslatef(0, 0.1, -0.4);
        glScalef(1.1, 0.05, 1.9);
        self.draw_box(1, 1, 1);
        glPopMatrix()

        self.draw_nose_w02()

        # Asa dianteira
        glColor3f(0.75, 0.75, 0.75);
        glPushMatrix();
        glTranslatef(0, 0.02, 1.65);
        glScalef(1.3, 0.05, 0.3);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        for x in [-0.65, 0.65]:
            glPushMatrix();
            glTranslatef(x, 0.07, 1.65);
            glScalef(0.02, 0.15, 0.3);
            self.draw_box(1, 1, 1);
            glPopMatrix()

        self.draw_rear_wing_structure()

        # Caixa de admissão e Luz de Freio
        glColor3f(0.15, 0.15, 0.15);
        glPushMatrix();
        glTranslatef(0, 0.45, 0.10);
        glScalef(0.14, 0.18, 0.15);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glColor3f(0.2, 0.2, 0.2);
        glPushMatrix();
        glTranslatef(0, 0.58, 0.1);
        glScalef(0.15, 0.1, 0.2);
        self.draw_box(1, 1, 1);
        glPopMatrix()
        glColor3f(1.0, 0.0, 0.0);
        glPushMatrix();
        glTranslatef(0, 0.25, -1.28);
        self.draw_box(0.08, 0.08, 0.02);
        glPopMatrix()

        glPopMatrix()

    def update(self, speed, delta_time):
        if self.speed > 0:
            self.wheel_rotation += self.speed * 500 * delta_time
            if self.wheel_rotation >= 360: self.wheel_rotation -= 360


# ---------------------------------------------------------------------------
# CLASSE Track
# ---------------------------------------------------------------------------
class Track:
    def __init__(self):
        self.offset = 0

    def draw_sky(self):
        glDisable(GL_LIGHTING);
        glDisable(GL_DEPTH_TEST);
        glMatrixMode(GL_PROJECTION);
        glPushMatrix();
        glLoadIdentity();
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity()
        glBegin(GL_QUADS)
        glColor3f(0.3, 0.5, 0.9);
        glVertex3f(-1, 1, 0.5);
        glVertex3f(1, 1, 0.5);
        glColor3f(0.6, 0.8, 1.0);
        glVertex3f(1, -0.2, 0.5);
        glVertex3f(-1, -0.2, 0.5)
        glEnd()
        glBegin(GL_QUADS)
        glColor3f(0.6, 0.8, 1.0);
        glVertex3f(-1, -0.2, 0.5);
        glVertex3f(1, -0.2, 0.5);
        glColor3f(0.7, 0.85, 0.9);
        glVertex3f(1, -1, 0.5);
        glVertex3f(-1, -1, 0.5)
        glEnd()
        glPopMatrix();
        glMatrixMode(GL_PROJECTION);
        glPopMatrix();
        glMatrixMode(GL_MODELVIEW);
        glEnable(GL_DEPTH_TEST);
        glEnable(GL_LIGHTING)

    def draw_clouds(self):
        glDisable(GL_LIGHTING);
        glColor4f(1.0, 1.0, 1.0, 0.7)
        cloud_positions = [(10, 15, 20), (-15, 18, 30), (20, 16, -10), (-8, 17, 40), (15, 19, 50), (-20, 16, 15),
                           (5, 20, -20)]
        for x, y, z in cloud_positions:
            glPushMatrix();
            glTranslatef(x, y, z + self.offset * 0.1)
            for i in range(5):
                glPushMatrix();
                offset_x = (i - 2) * 1.5;
                offset_y = math.sin(i * 0.5) * 0.5;
                glTranslatef(offset_x, offset_y, 0);
                self.draw_sphere(1.0 + math.sin(i) * 0.3);
                glPopMatrix()
            glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_sphere(self, radius):
        slices = 10;
        stacks = 10
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks);
            z0 = radius * math.sin(lat0);
            zr0 = radius * math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks);
            z1 = radius * math.sin(lat1);
            zr1 = radius * math.cos(lat1)
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices;
                x = math.cos(lng);
                y = math.sin(lng)
                glVertex3f(x * zr0, y * zr0, z0);
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def draw(self):
        self.draw_sky();
        self.draw_clouds();
        glColor3f(0.3, 0.3, 0.3);
        glPushMatrix();
        glTranslatef(0, 0, self.offset)
        glNormal3f(0, 1, 0)
        for i in range(-2, 25):
            glPushMatrix();
            glTranslatef(0, 0, i * 20)
            glBegin(GL_QUADS);
            glVertex3f(-3, 0, -10);
            glVertex3f(3, 0, -10);
            glVertex3f(3, 0, 10);
            glVertex3f(-3, 0, 10);
            glEnd();
            glPopMatrix()
            glColor3f(1, 1, 1)
            for x_pos in [-3, 3]:
                glPushMatrix();
                glTranslatef(x_pos, 0.01, i * 20)
                glBegin(GL_QUADS);
                glVertex3f(-0.1, 0, -10);
                glVertex3f(0.1, 0, -10);
                glVertex3f(0.1, 0, 10);
                glVertex3f(-0.1, 0, 10);
                glEnd();
                glPopMatrix()
            glColor3f(0.9, 0.9, 0.2)
            for j in range(-5, 6, 2):
                glPushMatrix();
                glTranslatef(0, 0.01, i * 20 + j * 2)
                glBegin(GL_QUADS);
                glVertex3f(-0.05, 0, -0.8);
                glVertex3f(0.05, 0, -0.8);
                glVertex3f(0.05, 0, 0.8);
                glVertex3f(-0.05, 0, 0.8);
                glEnd();
                glPopMatrix()
            glColor3f(0.3, 0.3, 0.3)
        glPopMatrix()
        glColor3f(0.2, 0.6, 0.2)
        for x_pos in [-8, 8]:
            glPushMatrix();
            glTranslatef(x_pos, -0.01, self.offset);
            glNormal3f(0, 1, 0)
            for i in range(-2, 25):
                glPushMatrix();
                glTranslatef(0, 0, i * 20)
                glBegin(GL_QUADS);
                glVertex3f(-5, 0, -10);
                glVertex3f(5, 0, -10);
                glVertex3f(5, 0, 10);
                glVertex3f(-5, 0, 10);
                glEnd();
                glPopMatrix()
            glPopMatrix()
        glColor3f(0.8, 0.1, 0.1)
        for x_pos in [-6, 6]:
            glPushMatrix();
            glTranslatef(x_pos, 0.3, self.offset)
            for i in range(-2, 25):
                glPushMatrix();
                glTranslatef(0, 0, i * 20)
                for j in range(-5, 6, 2):
                    glPushMatrix();
                    glTranslatef(0, 0, j * 2);
                    glScalef(0.3, 0.6, 1.5);
                    self.draw_box(1, 1, 1);
                    glPopMatrix()
                glPopMatrix()
            glPopMatrix()

    def draw_box(self, width, height, depth):
        w, h, d = width / 2, height / 2, depth / 2
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1);
        glVertex3f(-w, -h, d);
        glVertex3f(w, -h, d);
        glVertex3f(w, h, d);
        glVertex3f(-w, h, d)
        glNormal3f(0, 0, -1);
        glVertex3f(-w, -h, -d);
        glVertex3f(-w, h, -d);
        glVertex3f(w, h, -d);
        glVertex3f(w, -h, -d)
        glNormal3f(0, 1, 0);
        glVertex3f(-w, h, d);
        glVertex3f(w, h, d);
        glVertex3f(w, h, -d);
        glVertex3f(-w, h, -d)
        glNormal3f(0, -1, 0);
        glVertex3f(-w, -h, d);
        glVertex3f(-w, -h, -d);
        glVertex3f(w, -h, -d);
        glVertex3f(w, -h, d)
        glNormal3f(1, 0, 0);
        glVertex3f(w, -h, -d);
        glVertex3f(w, h, -d);
        glVertex3f(w, h, d);
        glVertex3f(w, -h, d)
        glNormal3f(-1, 0, 0);
        glVertex3f(-w, -h, -d);
        glVertex3f(-w, -h, d);
        glVertex3f(-w, h, d);
        glVertex3f(-w, h, -d)
        glEnd()

    def update(self, speed, delta_time):
        self.offset -= (speed * 0.3) * delta_time
        if self.offset <= -20: self.offset += 20


# ---------------------------------------------------------------------------
# CLASSE F1Simulation
# ---------------------------------------------------------------------------
class F1Simulation:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.width = 800;
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("Mercedes MGP W02 2011 - F1 Simulator")
        glEnable(GL_DEPTH_TEST);
        glClearColor(0.6, 0.8, 1.0, 1.0);
        glEnable(GL_NORMALIZE)
        glEnable(GL_FOG);
        glFogfv(GL_FOG_COLOR, [0.6, 0.8, 1.0, 1.0]);
        glFogi(GL_FOG_MODE, GL_LINEAR);
        glFogf(GL_FOG_START, 50.0);
        glFogf(GL_FOG_END, 300.0)
        glMatrixMode(GL_PROJECTION);
        gluPerspective(45, self.width / self.height, 0.1, 350.0);
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 10, 5, 1]);
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1]);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        glEnable(GL_COLOR_MATERIAL);
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0]);
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10.0)

        # Carregar texturas
        self.tire_texture_id = load_texture("pirelli_texture.png")
        self.petronas_texture_id = load_texture("petronas.png")
        self.aabar_texture_id = load_texture("aabar.png")
        self.mercedes_texture_id = load_texture("logomeca.png")
        self.seven_tex_id = load_texture("7.png")

        # Som do Motor
        self.engine_sound = None
        if os.path.exists("f1.mp3"):
            try:
                self.engine_sound = pygame.mixer.Sound("f1.mp3")
                self.engine_sound.set_volume(0.5)
            except Exception as e:
                print(f"Erro ao carregar f1.mp3: {e}")
        else:
            print("Aviso: 'f1.mp3' não encontrado na pasta!")
        self.is_sound_playing = False

        self.car = F1Car(self.tire_texture_id, self.petronas_texture_id, self.aabar_texture_id,
                         self.mercedes_texture_id, self.seven_tex_id)
        self.track = Track()
        self.clock = pygame.time.Clock();
        self.running = False
        self.font = pygame.font.Font(None, 36);
        self.small_font = pygame.font.Font(None, 24)
        self.camera_angle = 0;
        self.camera_pitch = 20;
        self.camera_distance = 8
        self.drs_target = 0

    def draw_text(self, text, x, y, font=None, color=(255, 255, 255)):
        if font is None: font = self.font
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glMatrixMode(GL_PROJECTION);
        glPushMatrix();
        glLoadIdentity();
        glOrtho(0, self.width, self.height, 0, -1, 1);
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity()
        glDisable(GL_LIGHTING);
        glDisable(GL_DEPTH_TEST);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glRasterPos2f(x, y);
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND);
        glEnable(GL_DEPTH_TEST);
        glEnable(GL_LIGHTING);
        glPopMatrix();
        glMatrixMode(GL_PROJECTION);
        glPopMatrix();
        glMatrixMode(GL_MODELVIEW)

    def draw_ui(self):
        status = "CORRENDO" if self.running else "PARADO"
        speed_kmh = int(self.car.speed)
        drs_status = "ABERTO" if self.car.drs_open else "FECHADO"
        self.draw_text(f"Mercedes MGP W02 - 2011", 20, 30)
        self.draw_text(f"Status: {status}", 20, 70, self.small_font, (0, 255, 0) if self.running else (255, 0, 0))
        self.draw_text(f"Velocidade: {speed_kmh} km/h", 20, 100, self.small_font)
        self.draw_text(f"DRS: {drs_status}", 20, 130, self.small_font,
                       (0, 255, 0) if self.car.drs_open else (255, 255, 255))
        y_offset = self.height - 230
        self.draw_text("CONTROLES:", 20, y_offset, self.small_font, (255, 255, 0))
        self.draw_text("ESPACO - Iniciar/Parar", 20, y_offset + 30, self.small_font)
        self.draw_text("SETA CIMA - Acelerar", 20, y_offset + 60, self.small_font)
        self.draw_text("SETA BAIXO - Frear", 20, y_offset + 90, self.small_font)
        self.draw_text("A/D - Girar camera", 20, y_offset + 120, self.small_font)
        self.draw_text("W/S - Altura da camera", 20, y_offset + 150, self.small_font)
        self.draw_text("Z/X - Zoom camera", 20, y_offset + 180, self.small_font)
        self.draw_text("SHIFT - DRS (asa movel)", 20, y_offset + 210, self.small_font)
        self.draw_text("ESC - Sair", 20, y_offset + 240, self.small_font)

    def run(self):
        while True:
            delta_time = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == QUIT: pygame.quit(); return
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: pygame.quit(); return
                    if event.key == K_SPACE:
                        self.running = not self.running;
                        if self.running:
                            self.car.speed = 2.0
                        else:
                            self.car.speed = 0
                    if event.key == K_LSHIFT or event.key == K_RSHIFT:
                        if not self.car.drs_open:
                            self.drs_target = self.car.speed + 30.0
                            if self.drs_target > 180.0: self.drs_target = 180.0
                        self.car.drs_open = not self.car.drs_open
                if event.type == VIDEORESIZE:
                    self.width, self.height = event.size;
                    self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL | RESIZABLE);
                    glViewport(0, 0, self.width, self.height);
                    glMatrixMode(GL_PROJECTION);
                    glLoadIdentity()
                    if self.height > 0: gluPerspective(45, self.width / self.height, 0.1, 350.0)
                    glMatrixMode(GL_MODELVIEW)

            keys = pygame.key.get_pressed()
            if self.running:
                limit = 180.0 if self.car.drs_open else 150.0
                if self.car.drs_open and self.car.speed < self.drs_target: self.car.speed += 15.0 * delta_time
                if not self.car.drs_open and self.car.speed > 150.0: self.car.speed -= 20.0 * delta_time
                if keys[K_UP]: self.car.speed += 25.0 * delta_time
                if keys[K_DOWN]: self.car.speed -= 50.0 * delta_time
                if self.car.speed > limit: self.car.speed = limit
                if self.car.speed < 0: self.car.speed = 0

            # Som do Motor
            if self.engine_sound:
                if self.car.speed > 0 and not self.is_sound_playing:
                    self.engine_sound.play(loops=-1);
                    self.is_sound_playing = True
                elif self.car.speed == 0 and self.is_sound_playing:
                    self.engine_sound.stop();
                    self.is_sound_playing = False

            if keys[K_a]: self.camera_angle -= 90 * delta_time
            if keys[K_d]: self.camera_angle += 90 * delta_time
            if keys[K_w]: self.camera_pitch = min(self.camera_pitch + 90 * delta_time, 89.0)
            if keys[K_s]: self.camera_pitch = max(self.camera_pitch - 90 * delta_time, 5.0)
            if keys[K_z] and self.camera_distance > 3: self.camera_distance -= 3 * delta_time
            if keys[K_x] and self.camera_distance < 15: self.camera_distance += 3 * delta_time

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
            glLoadIdentity()
            yaw_rad = math.radians(self.camera_angle);
            pitch_rad = math.radians(self.camera_pitch)
            h_dist = self.camera_distance * math.cos(pitch_rad);
            v_dist = self.camera_distance * math.sin(pitch_rad)
            cam_x = self.car.position[0] + h_dist * math.sin(yaw_rad);
            cam_z = self.car.position[2] - h_dist * math.cos(yaw_rad);
            cam_y = self.car.position[1] + v_dist
            gluLookAt(cam_x, cam_y, cam_z, self.car.position[0], self.car.position[1], self.car.position[2], 0, 1, 0)

            self.track.draw();
            self.car.draw()
            if self.running: self.car.update(self.car.speed, delta_time); self.track.update(self.car.speed, delta_time)
            self.draw_ui();
            pygame.display.flip()


if __name__ == "__main__":
    sim = F1Simulation()
    sim.run()