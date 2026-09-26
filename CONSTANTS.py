POLYGONS_AMOUNT = 300
TARGET_HEIGHT = 200
CONTENDERS_AMOUNT = 2  # one parent and one child per epoch: a (1+1) hill climber
SIDES_POLYGONS = 3
MIN_RADIUS = 3
MAX_RADIUS = 30
SIGMA_X = 5
SIGMA_Y = 5
SIGMA_RGB = 40
SIGMA_ANGLE = 30
SIGMA_RADIUS = 0.3  # multiplicative: radius *= exp(gauss(0, SIGMA_RADIUS))
N_POLYGONS_TO_MUTATE = 1
N_EPOCHS = 50000
SNAPSHOT_EVERY = 500  # about 100 snapshots for the viewer
SIGMA_DECAY = True
SIGMA_FINAL_SCALE = 0.05  # sigma of the last epoch, as a fraction of the above
IMAGE_PATH = "mona_lisa.jpg"
