# source http://www.icub.org/software_documentation/icub_python_simworld_control.html
# extended with model import/manipulation, get hand position and screen movement

import collections
import yarp
yarp.Network.init()  # Initialise YARP


########################################################
class WorldController:
    """Class for controlling iCub simulator via its RPC world port."""

    def __init__(self):
        self._rpc_client = yarp.RpcClient()
        self._port_name = "/WorldController-" + str(id(self)) + "/commands"
        self._rpc_client.open(self._port_name)
        self._rpc_client.addOutput("/icubSim/world")

        # A dictionary to track simulator object IDs for all types of objects
        self._sim_ids_counters = collections.defaultdict(lambda: 0)
        self._sim_mids_counters = collections.defaultdict(lambda: 0)

        # A sequence to track internal object IDs. This list stores tuples (object type, simulator id)
        # so that outside one does not have to remember the type of object.
        self._objects = []
        self._models = []

    def _execute(self, cmd):
        """Execute an RPC command, returning obtained answer bottle."""
        ans = yarp.Bottle()
        self._rpc_client.write(cmd, ans)
        return ans

    def _is_success(self, ans):
        """Check if RPC call answer Bottle indicates successfull execution."""
        return ans.size() == 1 and ans.get(0).asVocab() == 27503  # Vocab for '[ok]'

    def _prepare_del_all_command(self):
        """Prepare the "world del all" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "del", "all"]))
        return result

    def del_all(self):
        """Delete all objects and models from the simulator"""
        result = self._is_success(self._execute(self._prepare_del_all_command()))

        if result:
            # Clear the counters
            self._sim_ids_counters.clear()
            self._sim_mids_counters.clear()
            del self._objects[:]
            del self._models[:]
        return result

########################################################
########### object creation and manipulation ###########
########################################################

    ########################################################
    ########## create object inside the simulator ##########
    def _prepare_create_obj_command(self, obj, size, location, colour):
        """Prepare an RPC command for creating an object in the simulator environment.

        See Simulator Readme section 'Object Creation'

        Parameters:
            obj         -- object type string. 'sph', 'box', 'cyl' 'ssph', 'sbox' or 'scyl'.
            size        -- list of values specifying the size of an object. Parameters depend on object type:
                            (s)box: [ x, y, z ]
                            (s)sph: [ radius ]
                            (s)cyl: [ radius, length ]
            location    -- coordinates of the object location, [ x, y, z ]
            colour      -- object colour in RGB (normalised), [ r, g, b ]
        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """

        result = yarp.Bottle()
        result.clear()

        list(map(result.addString, ["world", "mk", obj]))
        list(map(result.addDouble, size))
        list(map(result.addDouble, location))
        list(map(result.addDouble, colour))
        return result

    def create_object(self, obj, size, location, colour):
        """Create an object of a specified type, size, location and colour, returning internal object ID or -1 on error."""

        cmd = self._prepare_create_obj_command(obj, size, location, colour)

        if self._is_success(self._execute(cmd)):
            obj_sim_id = self._sim_ids_counters[obj] + 1  # iCub simulator IDs start from 1

            # Update the counters

            self._sim_ids_counters[obj] += 1
            self._objects.append((obj, obj_sim_id))

            # Internal object IDs are shared among all types of objects and start from 0;
            # they are essentially indices of the self._objects sequence
            return len(self._objects) - 1
        else:
            print('error')
            return -1  # error

    ########################################################
    ########### move object inside the simulator ###########
    def _prepare_move_command_obj(self, obj, obj_id, location):
        """Prepare the "world set <obj> <xyz>" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", obj]))
        result.addInt(obj_id)
        list(map(result.addDouble, location))
        return result

    def move_object(self, obj_id, location):
        """Move an object specified by the internal id to another location."""
        obj_desc = self._objects[obj_id]
        return self._is_success(self._execute(self._prepare_move_command_obj(obj_desc[0], obj_desc[1], location)))

    ########################################################
    ####### get object position inside the simulator #######
    def _prepare_get_pos_command_obj(self, obj, obj_id):
        """Prepare the "world get <obj> <id>" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", obj]))
        result.addInt(obj_id)
        return result

    def get_object_location(self, obj_id):
        """Obtain the object location from the simulator. Returns None on failure."""
        obj_desc = self._objects[obj_id]
        result = self._execute(self._prepare_get_pos_command_obj(obj_desc[0], obj_desc[1]))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz coordinates
        else:
            return None  # An error occured

    ########################################################
    ########## rotate object inside the simulator ##########
    def _prepare_rot_command_obj(self, obj, obj_id, orientation):
        """Prepare the "world set <obj> <xyz>" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", obj]))
        result.addInt(obj_id)
        list(map(result.addDouble, orientation))
        return result

    def rotate_object(self, obj_id, orientation):
        """Move an object specified by the internal id to another location."""
        obj_desc = self._objects[obj_id]
        return self._is_success(self._execute(self._prepare_rot_command_obj(obj_desc[0], obj_desc[1], orientation)))

    ########################################################
    ##### get object orientation inside the simulator ######
    def _prepare_get_rot_command_obj(self, obj, obj_id):
        """Prepare the "world get <obj> <id>" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", obj]))
        result.addInt(obj_id)
        return result

    def get_object_orientation(self, obj_id):
        """Obtain the object location from the simulator. Returns None on failure."""
        obj_desc = self._objects[obj_id]
        result = self._execute(self._prepare_get_rot_command_obj(obj_desc[0], obj_desc[1]))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz angles
        else:
            return None  # An error occured


########################################################
########### model creation and manipulation ############
########################################################

    ########################################################
    ########### load 3D model into the simulator ###########

    def _prepare_create_command_model(self, m_type, model, texture, location):
        """Prepare an RPC command for importing a model in the simulator environment.

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            model       -- model file name, for example 'model.x' (only type .x)
            texture     -- texture file name, for example 'gruen.bmp' (only type .bmp)
            location    -- coordinates of the model location, [ x, y, z ]
        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "mk", m_type, model, texture]))
        list(map(result.addDouble, location))
        return result

    def create_model(self, m_type, model, texture, location):
        """
        Import a model of a specified type, texture and location

        See Simulator Readme section 'Importing 3D models into the simulator'

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            model       -- model file name, for example 'model.x' (only type .x)
            texture     -- texture file name, for example 'gruen.bmp' (only type .bmp)
            location    -- coordinates of the model location, [ x, y, z ]
        Returns:
            internal model ID to reference the model or -1 on error

        """

        cmd = self._prepare_create_command_model(m_type, model, texture, location)
        if self._is_success(self._execute(cmd)):
            mod_sim_id = self._sim_mids_counters[m_type] + 1  # iCub simulator IDs start from 1

            # Update the counters
            self._sim_mids_counters[m_type] += 1
            self._models.append((m_type, mod_sim_id))

            # Internal model IDs are shared among all models and start from 0;
            # they are essentially indices of the self._models sequence
            return len(self._models) - 1
        else:
            return -1  # error

    ########################################################
    ########### move model inside the simulator ############
    def _prepare_move_command_model(self, m_type, mod_id, location):
        """
        Prepare the "world set <mod> <xyz>" command bottle.

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            mod_id      -- simulator model ID
            location    -- coordinates of the model location, [ x, y, z ]
        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", m_type]))
        result.addInt(mod_id)
        list(map(result.addDouble, location))
        return result

    def move_model(self, mod_id, location):
        """
        Move a model specified by the internal id to another location.

        Parameters:
            mod_id      -- internal model ID
            location    -- coordinates of the model location, [ x, y, z ]

        """
        mod_desc = self._models[mod_id]
        return self._is_success(self._execute(self._prepare_move_command_model(mod_desc[0], mod_desc[1], location)))

    ########################################################
    ####### get model position inside the simulator ########
    def _prepare_get_pos_command_model(self, m_type, mod_id):
        """
        Prepare the "world get <mod> <id>" command bottle.

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            mod_id      -- simulator model ID

        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", m_type]))
        result.addInt(mod_id)
        return result

    def get_model_location(self, mod_id):
        """
        Obtain the model location from the simulator. Returns None on failure.

        Parameters:
            mod_id      -- internal model ID

         Returns:
             model location coordinates [x, y, z]

        """
        mod_desc = self._models[mod_id]
        result = self._execute(self._prepare_get_pos_command_model(mod_desc[0], mod_desc[1]))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz coordinates
        else:
            return None  # An error occured

    ########################################################
    ########## rotate model inside the simulator ###########
    def _prepare_rot_command_model(self, m_type, mod_id, orientation):
        """
        Prepare the "world rot <mod> <rotx roty rotz>" command bottle.

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            mod_id      -- simulator model ID
            orientation -- new model orientation [rotx, roty, rotz]

        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", m_type]))
        result.addInt(mod_id)
        list(map(result.addDouble, orientation))
        return result

    def rotate_model(self, mod_id, orientation):
        """
        Move a model specified by the internal id to another location.

        Parameters:
            mod_id      -- internal model ID
            orientation -- new model orientation [rotx, roty, rotz]
        """

        mod_desc = self._models[mod_id]
        return self._is_success(self._execute(self._prepare_rot_command_model(mod_desc[0], mod_desc[1], orientation)))

    ########################################################
    ###### get model orientation inside the simulator ######
    def _prepare_get_rot_command_model(self, m_type, mod_id):
        """
        Prepare the "world rot <mod> <id>" command bottle.

        Parameters:
            m_type      -- model type as string: 'smodel', 'model'
            mod_id      -- simulator model ID

        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", m_type]))
        result.addInt(mod_id)
        return result

    def get_model_orientation(self, mod_id):
        """
        Obtain the model rotation from the simulator. Returns None on failure.

        Parameters:
            mod_id      -- internal model ID

         Returns:
             model orientation [rotx, roty, rotz]

        """

        mod_desc = self._models[mod_id]
        result = self._execute(self._prepare_get_rot_command_model(mod_desc[0], mod_desc[1]))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz angles
        else:
            return None  # An error occured

    ########################################################
    ######### get path to model and texture files ##########
    def _prepare_get_path_command_model(self):
        """
        Prepare the "world get mdir" command bottle.

        Returns:
            yarp.Bottle with the command, ready to be sent to the rpc port of the simulator

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", "mdir"]))
        return result

    def get_model_path(self):
        """
        Obtain the path to model and texture files. Returns None on failure.

        Returns:
             full set path to model and texture files

        """

        result = self._execute(self._prepare_get_path_command_model())
        if result.size() == 1:
            return result.get(0).asString()  # path to model and texture files
        else:
            return None  # An error occured

    ########################################################
    ######### set path to model and texture files ##########
    def _prepare_set_path_command_model(self, path):
        """
        Prepare the "world set mdir" command bottle.

        Parameters:
            path      -- new path to model and texture files

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", "mdir", path]))
        return result

    def set_model_path(self, path):
        """
        Obtain the path to model and texture files. Returns None on failure.

        Parameters:
            path      -- new path to model and texture files

        """

        return self._is_success(self._execute(self._prepare_set_path_command_model(path)))

########################################################
################### special commands ###################
########################################################

    ########################################################
    ################## get hand position ###################
    def _prepare_get_command_hand(self, hand):
        """
        Prepare the "world get <hand>" command bottle.

        Parameters:
            hand      -- string 'lhand' or 'rhand', defines the which hand is choosen

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", hand]))
        return result

    def get_hand_location(self, hand):
        """
        Obtain the hand location from the simulator. Returns None on failure.

        Parameters:
            hand      -- string 'lhand' or 'rhand', defines the which hand is choosen

        Returns:
             hand location coordinates [x, y, z]

        """

        result = self._execute(self._prepare_get_command_hand(hand))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz coordinates
        else:
            return None  # An error occured

    ########################################################
    ################# get screen position ##################
    def _prepare_get_command_screen(self):
        """
        Prepare the "world get screen" command bottle.


        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", "screen"]))
        return result

    def get_screen_location(self):
        """
        Obtain the screen location from the simulator. Returns None on failure.


        Returns:
             screen location coordinates [x, y, z]

        """

        result = self._execute(self._prepare_get_command_screen())
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz coordinates
        else:
            return None  # An error occured

    ########################################################
    ################# set screen position ##################
    def _prepare_set_command_screen(self, location):
        """
        Prepare the "world set screen <location>" command bottle.


        Parameter:
            location        --screen location coordinates [x, y, z]

        """

        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", "screen"]))
        list(map(result.addDouble, location))
        return result

    def set_screen_location(self, location):
        """
        Set the screen inside simulator to a new position. Returns None on failure.


        Parameter:
            location        --screen location coordinates [x, y, z]

        """

        result = self._execute(self._prepare_get_command_screen(location))
        if result.size() == 3:
            return [result.get(i).asDouble() for i in range(3)]  # 3-element list with xyz coordinates
        else:
            return None  # An error occured

########################################################
################### call destructor ####################
    def __del__(self):
        try:
            if self._rpc_client is not None:
                self.del_all()
            self._rpc_client.close()
            del self._rpc_client
        except AttributeError:
            pass
