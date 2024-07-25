"""Defines the MJX environment class."""

import numpy as np
from gym import utils, spaces
import gym
from gym.envs.mujoco import mujoco_env
import os


from collections import OrderedDict
import os


from gym import error, spaces
from gym.utils import seeding
import numpy as np
from os import path
import gym

try:
    import mujoco_py
except ImportError as e:
    raise error.DependencyNotInstalled(
        "{}. (HINT: you need to install mujoco_py, and also perform the setup instructions here: https://github.com/openai/mujoco-py/.)".format(
            e
        )
    )

###### Robot Env ######


class RobotMujocoEnv(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self):
        # Ensure the model path is correct
        model_path = os.path.join(os.path.dirname(__file__), "assets", "h1.xml")

        # Load the model first
        self.model = mujoco_py.load_model_from_path(model_path)
        self.sim = mujoco_py.MjSim(self.model)
        self.data = self.sim.data
        self.viewer = None
        self._viewers = {}

        # Now we can calculate the observation space
        obs_dim = self.model.nq - 1 + self.model.nv  # Excluding the first position from qpos
        observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float64)

        self.frame_skip = 4
        self.metadata = {
            "render_modes": [
                "human",
                "rgb_array",
                "depth_array",
            ],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

        # Initialize MujocoEnv with the calculated observation space
        mujoco_env.MujocoEnv.__init__(
            self,
            model_path,
            self.frame_skip, 
            observation_space=observation_space,
        )
        utils.EzPickle.__init__(self)

    # NOTE: need to make equal to observation_space set in step
    def _get_obs(self):
        data = self.sim.data
        return np.concatenate(
            [
                data.qpos.flat[2:],
                data.qvel.flat,
                data.cinert.flat,
                data.cvel.flat,
                data.qfrc_actuator.flat,
                data.cfrc_ext.flat,
            ]
        )

    def step(self, a):
        self.do_simulation(a, self.frame_skip)
        pos_after = self.sim.data.qpos[2]
        data = self.sim.data
        uph_cost = (pos_after - 0) / self.model.opt.timestep

        quad_ctrl_cost = 0.1 * np.square(data.ctrl).sum()
        quad_impact_cost = 0.5e-6 * np.square(data.cfrc_ext).sum()
        quad_impact_cost = min(quad_impact_cost, 10)
        reward = uph_cost - quad_ctrl_cost - quad_impact_cost + 1

        done = bool(False)
        return (
            self._get_obs(),
            reward,
            done,
            dict(reward_linup=uph_cost, reward_quadctrl=-quad_ctrl_cost, reward_impact=-quad_impact_cost),
        )

    def reset_model(self):
        c = 0.01
        self.set_state(
            self.init_qpos + self.np_random.uniform(low=-c, high=c, size=self.model.nq),
            self.init_qvel
            + self.np_random.uniform(
                low=-c,
                high=c,
                size=self.model.nv,
            ),
        )
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.trackbodyid = 1
        self.viewer.cam.distance = self.model.stat.extent * 1.0
        self.viewer.cam.lookat[2] = 0.8925
        self.viewer.cam.elevation = -20


# DEFAULT_SIZE = 500


# def convert_observation_to_space(observation):
#     if isinstance(observation, dict):
#         space = spaces.Dict(
#             OrderedDict([(key, convert_observation_to_space(value)) for key, value in observation.items()])
#         )
#     elif isinstance(observation, np.ndarray):
#         low = np.full(observation.shape, -float("inf"), dtype=np.float32)
#         high = np.full(observation.shape, float("inf"), dtype=np.float32)
#         space = spaces.Box(low, high, dtype=observation.dtype)
#     else:
#         raise NotImplementedError(type(observation), observation)

#     return space


# class MujocoEnv(gym.Env):
#     """Superclass for all MuJoCo environments."""

#     def __init__(self, model_path, frame_skip):
#         if model_path.startswith("/"):
#             fullpath = model_path
#         else:
#             fullpath = os.path.join(os.path.dirname(__file__), model_path)
#         if not path.exists(fullpath):
#             raise IOError("File %s does not exist" % fullpath)
#         self.frame_skip = frame_skip
#         self.model = mujoco_py.load_model_from_path(fullpath)
#         self.sim = mujoco_py.MjSim(self.model)
#         self.data = self.sim.data
#         self.viewer = None
#         self._viewers = {}

#         self.metadata = {
#             "render_modes": [
#                 "human",
#                 "rgb_array",
#                 "depth_array",
#             ],
#             "video_frames_per_second": int(np.round(1.0 / self.dt)),
#         }

#         self.init_qpos = self.sim.data.qpos.ravel().copy()
#         self.init_qvel = self.sim.data.qvel.ravel().copy()

#         self._set_action_space()

#         action = self.action_space.sample()
#         observation, _reward, done, _info = self.step(action)
#         print(observation, _reward, done, _info)
#         assert not done

#         self._set_observation_space(observation)

#         self.seed()

#     def _set_action_space(self):
#         bounds = self.model.actuator_ctrlrange.copy().astype(np.float32)
#         low, high = bounds.T
#         self.action_space = spaces.Box(low=low, high=high, dtype=np.float32)
#         return self.action_space

#     def _set_observation_space(self, observation):
#         self.observation_space = convert_observation_to_space(observation)
#         return self.observation_space

#     def seed(self, seed=None):
#         self.np_random, seed = seeding.np_random(seed)
#         return [seed]

#     # methods to override:
#     # ----------------------------

#     def reset_model(self):
#         """
#         Reset the robot degrees of freedom (qpos and qvel).
#         Implement this in each subclass.
#         """
#         raise NotImplementedError

#     def viewer_setup(self):
#         """
#         This method is called when the viewer is initialized.
#         Optionally implement this method, if you need to tinker with camera position
#         and so forth.
#         """
#         pass

#     # -----------------------------

#     def reset(self):
#         self.sim.reset()
#         ob = self.reset_model()
#         return ob

#     def set_state(self, qpos, qvel):
#         assert qpos.shape == (self.model.nq,) and qvel.shape == (self.model.nv,)
#         old_state = self.sim.get_state()
#         new_state = mujoco_py.MjSimState(old_state.time, qpos, qvel, old_state.act, old_state.udd_state)
#         self.sim.set_state(new_state)
#         self.sim.forward()

#     @property
#     def dt(self):
#         return self.model.opt.timestep * self.frame_skip

#     def do_simulation(self, ctrl, n_frames):
#         self.sim.data.ctrl[:] = ctrl
#         for _ in range(n_frames):
#             self.sim.step()

#     def render(self, mode="human", width=DEFAULT_SIZE, height=DEFAULT_SIZE, camera_id=None, camera_name=None):
#         if mode == "rgb_array" or mode == "depth_array":
#             if camera_id is not None and camera_name is not None:
#                 raise ValueError("Both `camera_id` and `camera_name` cannot be" " specified at the same time.")

#             no_camera_specified = camera_name is None and camera_id is None
#             if no_camera_specified:
#                 camera_name = "track"

#             if camera_id is None and camera_name in self.model._camera_name2id:
#                 camera_id = self.model.camera_name2id(camera_name)

#             self._get_viewer(mode).render(width, height, camera_id=camera_id)

#         if mode == "rgb_array":
#             # window size used for old mujoco-py:
#             data = self._get_viewer(mode).read_pixels(width, height, depth=False)
#             # original image is upside-down, so flip it
#             return data[::-1, :, :]
#         elif mode == "depth_array":
#             self._get_viewer(mode).render(width, height)
#             # window size used for old mujoco-py:
#             # Extract depth part of the read_pixels() tuple
#             data = self._get_viewer(mode).read_pixels(width, height, depth=True)[1]
#             # original image is upside-down, so flip it
#             return data[::-1, :]
#         elif mode == "human":
#             self._get_viewer(mode).render()

#     def close(self):
#         if self.viewer is not None:
#             # self.viewer.finish()
#             self.viewer = None
#             self._viewers = {}

#     def _get_viewer(self, mode):
#         self.viewer = self._viewers.get(mode)
#         if self.viewer is None:
#             if mode == "human":
#                 self.viewer = mujoco_py.MjViewer(self.sim)
#             elif mode == "rgb_array" or mode == "depth_array":
#                 self.viewer = mujoco_py.MjRenderContextOffscreen(self.sim, -1)

#             self.viewer_setup()
#             self._viewers[mode] = self.viewer
#         return self.viewer

#     def get_body_com(self, body_name):
#         return self.data.get_body_xpos(body_name)

#     def state_vector(self):
#         return np.concatenate([self.sim.data.qpos.flat, self.sim.data.qvel.flat])
