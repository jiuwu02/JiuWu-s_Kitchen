# coding: UTF-8
import math
import random
import json
import re

import pyspigot as ps  # type: ignore

from org.bukkit import Location, Bukkit, Material, Sound, Registry, Particle, NamespacedKey  # type: ignore
from org.bukkit.util import Transformation  # type: ignore
from org.bukkit.block import BlockFace  # type: ignore
from org.bukkit.entity import Player, EntityType, ItemDisplay  # type: ignore
from org.bukkit.inventory import EquipmentSlot, ItemStack  # type: ignore
from org.bukkit.event.player import PlayerInteractEvent  # type: ignore
from org.bukkit.event.block import BlockBreakEvent, Action  # type: ignore

from java.lang import System  # type: ignore
from java.time import Duration  # type: ignore
from org.joml import Vector3f, Quaternionf  # type: ignore

from net.kyori.adventure.text import Component, TextReplacementConfig # type: ignore
from net.kyori.adventure.text.serializer.gson import GsonComponentSerializer # type: ignore
from net.kyori.adventure.text.serializer.plain import PlainTextComponentSerializer # type: ignore
from net.kyori.adventure.text.serializer.legacy import LegacyComponentSerializer # type: ignore
from net.kyori.adventure.text.minimessage import MiniMessage # type: ignore
from net.kyori.adventure.title import Title # type: ignore

class ConfigManager:
    '''配置文件管理类'''
    
    # 类变量，存储配置实例
    _config = None
    _choppingBoardRecipe = None
    _wokRecipe = None
    _data = None
    _prefix = None
    
    @staticmethod
    def _setConfigValue(configFile, path, defaultValue, comments=None):
        '''为配置项设置默认值和注释
        
        参数
            configFile: 配置文件对象
            path: 配置项路径
            defaultValue: 默认值
            comments: 注释列表(可选)
        '''
        if not configFile.contains(path):
            configFile.setIfNotExists(path, defaultValue)
            if comments is not None:
                configFile.setComments(path, comments)
    
    @staticmethod
    def _loadConfig():
        '''加载并初始化插件配置文件
        
        返回
            配置对象
        '''
        configPath = "JiuWu's Kitchen/Config.yml"
        configFile = ps.config.loadConfig(configPath)
        
        # 砧板设置
        ConfigManager._setConfigValue(configFile,"Setting.ChoppingBoard.Drop",True,[u"砧板处理完成后是否掉落成品"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.StealthInteraction", True, [
            u"是否需要在潜行状态下与砧板交互",
            u"启用时: 玩家必须潜行才能使用砧板功能",
            u"禁用时: 玩家可直接交互无需潜行"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.Custom", False, [
            u"是否使用自定义方块作为砧板",
            u"启用时: 使用兼容插件的方块 (例如: CraftEngine)",
            u"禁用时: 使用原版的方块",
            "",
            u"CraftEngine的方块: craftengine <Key>:<ID>"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.Material", "OAK_LOG")
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.SpaceRestriction", False, [
            u"砧板上方是否允许存在方块",
            u"启用时: 砧板上方有方块时无法使用",
            u"禁用时: 砧板上方允许存在方块"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Custom", False, [
            u"是否使用自定义刀具",
            u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
            u"禁用时: 使用原版物品",
            "",
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Enable", True, [
            u"是否启用砧板事件",
            u"启用时: 切菜时有概率切伤手指"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Chance", 10)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Value", 2)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Material", "IRON_AXE")
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Offset.X", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Offset.Y", 1.01)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Offset.Z", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.X", 90.0)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.Y", 0.0)
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.Z", 0.0, [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)"])
        ConfigManager._setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Scale", 0.5)
        
        # 炒锅设置
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Drop", True, [u"炒锅烹饪完成后是否掉落成品"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.StealthInteraction", True, [
            u"控制与炒锅交互是否需要潜行",
            "",
            u"启用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都需要潜行状态",
            u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"不需要\" 潜行状态",
            "",
            u"禁用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都不需要潜行状态",
            u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"需要\" 潜行状态"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Custom", False, [
            u"是否使用自定义炒锅方块",
            u"启用时: 使用兼容插件的方块(例如: CraftEngine)",
            u"禁用时: 使用原版方块",
            "",
            u"CraftEngine的方块: craftengine <Key>:<ID>"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Material", "IRON_BLOCK")
        ConfigManager._setConfigValue(
            configFile, "Setting.Wok.HeatControl", {"CAMPFIRE": 1,"MAGMA_BLOCK": 2,"LAVA": 3,},[
                u"定义不同热源的烹饪强度",
                u"数值越高代表火候越猛",
                "",
                u"支持 CraftEngine 插件的方块/家具",
                u"CraftEngine的方块: craftengine <Key>:<ID>: <火候大小>"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.NeedBowl", True, [
            u"控制从炒锅盛出成品是否需要碗",
            u"启用时: 必须手持碗才能盛出成品",
            u"禁用时: 空手即可直接盛出成品",
            u"注意: 如果启用则盛出操作是否要求潜行由 Setting.Wok.StealthInteraction 控制"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.InvalidRecipeOutput", "STONE", [
            u"该选项用于当玩家放入不完整或无效的食材组合时",
            u"将成品盛出后会得到这个物品作为失败产物"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Dalay", 5, [
            u"炒锅翻炒食材的延迟时间 (秒)",
            u"这个值应该小于 Setting.Wok.TimeOut"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Damage.Enable", True, [
            u"是否启用炒锅取出食材烫伤事件",
            u"启用时: 如果锅内存在食材并且已经翻炒过，这时候取出食材将会受到伤害",
            u"禁用时: 从炒锅取出食材时将不会受到任何伤害"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Damage.Value", 2)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Failure.Enable", True, [
            u"是否启用炒锅烹饪失败事件",
            u"启用时: 即使食材和步骤都正确，也有概率烹饪失败",
            u"禁用时: 只要食材和步骤正确，烹饪必定成功"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Failure.Chance", 5)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Failure.Type", "BONE_MEAL", [
            u"炒锅烹饪失败时生成的产物类型"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.TimeOut", 30, [
            u"单次翻炒操作后的最大等待时间 (秒)",
            u"每次翻炒操作后会重置此计时器",
            u"计时结束前未再次翻炒: 锅内食材会烧焦变为失败产物"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Spatula.Custom", False, [
            u"是否使用自定义炒菜铲",
            u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
            u"禁用时: 使用原版物品",
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.Spatula.Material", "IRON_SHOVEL")
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Offset.X", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Offset.Y", 1.01)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Offset.Z", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Rotation.X", 90.0)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Rotation.Y", 0.0)
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Rotation.Z", "0.0-90.0", [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)"])
        ConfigManager._setConfigValue(configFile, "Setting.Wok.DisplayEntity.Scale", 0.5)
        
        # 消息设置
        messages = {
            "Messages.Prefix": u"<gray>[ <dark_gray>JiuWu's Kitchen<gray> ]",
            "Messages.Load": u"{Prefix} <green>欢迎使用 JiuWu's Kitchen! 版本 {Version} 已准备就绪!",
            "Messages.Reload.LoadPlugin": u"{Prefix} <green>JiuWu's Kitchen 已重新加载!",
            "Messages.Reload.LoadChoppingBoardRecipe": u"{Prefix} <green>已备好 {Amount} 道砧板料理配方",
            "Messages.Reload.LoadWokRecipe": u"{Prefix} <green>已备好 {Amount} 道炒锅料理配方",
            "Messages.InvalidMaterial": u"{Prefix} <red>大厨，这个食材 {Material} 似乎不太对劲...",
            "Messages.WokTop": u"<gold>炒锅中的食材:",
            "Messages.WokContent": u" <gray>{ItemName} <dark_gray>× <yellow>{ItemAmount} <gray>翻炒次数: <yellow>{Count}",
            "Messages.WokDown": u"<gold>总计翻炒次数: <yellow>{Count}",
            "Messages.WokHeatControl": u"<gold>火候强度: <yellow>{Heat}级",
            "Messages.NoPermission": u"{Prefix} <red>大厨，你没有特殊的权限哦! ",
            "Messages.Title.CutHand.MainTitle": u"<red>哎哟! 切到手了! ",
            "Messages.Title.CutHand.SubTitle": u"<gray>小心刀具! 你受到了 <red>{Damage} <gray>点伤害",
            "Messages.Title.Scald.MainTitle": u"<red>沸沸沸! 烫烫烫! ",
            "Messages.Title.Scald.SubTitle": u"<gray>小心热锅! 你受到了 <red>{Damage} <gray>点伤害",
            "Messages.ActionBar.TakeOffItem": u"<gray>提示：空手轻点砧板可取下食材",
            "Messages.ActionBar.WokNoItem": u"<red>炒锅空空如也，快放些食材吧! ",
            "Messages.ActionBar.WokAddItem": u"<green>向炒锅中添加了 <white>{Material} <green>食材! ",
            "Messages.ActionBar.CutAmount": u"<gray>切菜进度: <green>{CurrentCount} <dark_gray>/ <green>{NeedCount}",
            "Messages.ActionBar.StirCount": u"<gray>翻炒次数: <green>{Count}",
            "Messages.ActionBar.ErrorRecipe": u"<red>哎呀，这道菜不是这么做的! 大厨再想想？",
            "Messages.ActionBar.FailureRecipe": u"<red>烹饪失败...食材浪费了，别灰心! ",
            "Messages.ActionBar.SuccessRecipe": u"<green>完美! 你成功烹饪了一道美味佳肴! ",
            "Messages.ActionBar.CannotCut": u"<red>大厨，这个食材不能在这里处理哦! ",
            "Messages.ActionBar.BurntFood": u"<red>哎呀! 火太大了，菜烧焦了! ",
            "Messages.ActionBar.StirFriedTooQuickly": u"<red>翻炒得太急了! 食材还没熟透呢! ",
            "Messages.ActionBar.WokStirItem": u"<green>正在翻炒 <gray>{Material}...",
            "Messages.PluginLoad.CraftEngine": u"{Prefix} <green>检测到 CraftEngine 插件",
            "Messages.PluginLoad.MMOItems": u"{Prefix} <green>检测到 MMOItems 插件"
        }
        
        for key, value in messages.items(): ConfigManager._setConfigValue(configFile, key, value)
        
        # 音效设置
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardAddItem", u"entity.item_frame.add_item", [u"砧板添加食材的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutItem", u"item.axe.strip", [u"砧板切割食材的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutHand", u"entity.player.hurt", [u"砧板切割时手被切伤的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.WokAddItem", u"block.anvil.hit", [u"炒锅添加食材的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.WokStirItem", u"block.lava.extinguish", [u"炒锅翻炒食材的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.WokScald", u"entity.player.hurt_on_fire", [u"炒锅翻炒时手被烫伤的音效"])
        ConfigManager._setConfigValue(
            configFile, "Setting.Sound.WokTakeOffItem", u"entity.item.pickup", [u"炒锅取出食材的音效"])
        
        # 粒子设置
        ConfigManager._setConfigValue(
            configFile, "Setting.Particle.ChoppingBoardCutItem.Type", "CLOUD",[u"砧板切割食材的粒子"])
        ConfigManager._setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Amount", 10)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetX", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetY", 1.0)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetZ", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Speed", 0.05)
        
        ConfigManager._setConfigValue(
            configFile, "Setting.Particle.WokStirItem.Type", "CAMPFIRE_COSY_SMOKE",[u"炒锅翻炒食材的粒子"])
        ConfigManager._setConfigValue(configFile, "Setting.Particle.WokStirItem.Amount", 10)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetX", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetY", 1.0)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetZ", 0.5)
        ConfigManager._setConfigValue(configFile, "Setting.Particle.WokStirItem.Speed", 0.05)
        
        configFile.save()
        return ps.config.loadConfig(configPath)
    
    @staticmethod
    def _loadChoppingBoardRecipe():
        '''加载砧板配方配置文件
        
        返回: 
            对象: 砧板配方文件
        '''
        choppingBoardRecipePath = "JiuWu's Kitchen/Recipe/ChoppingBoard.yml"
        return ps.config.loadConfig(choppingBoardRecipePath)
    
    @staticmethod
    def _loadWokRecipe():
        '''加载炒锅配方配置文件
        
        返回: 
            对象: 砧板配方文件
        '''
        wokRecipePath = "JiuWu's Kitchen/Recipe/Wok.yml"
        return ps.config.loadConfig(wokRecipePath)
    
    @staticmethod
    def _loadData():
        '''加载数据文件
        
        返回:
            对象: 数据文件
        '''
        dataPath = "JiuWu's Kitchen/Data.yml"
        return ps.config.loadConfig(dataPath)
    
    @staticmethod
    def getConfig():
        '''获取主配置对象'''
        if ConfigManager._config is None:
            ConfigManager._config = ConfigManager._loadConfig()
        return ConfigManager._config
    
    @staticmethod
    def getChoppingBoardRecipe():
        '''获取砧板配方配置'''
        if ConfigManager._choppingBoardRecipe is None:
            ConfigManager._choppingBoardRecipe = ConfigManager._loadChoppingBoardRecipe()
        return ConfigManager._choppingBoardRecipe
    
    @staticmethod
    def getWokRecipe():
        '''获取炒锅配方配置'''
        if ConfigManager._wokRecipe is None:
            ConfigManager._wokRecipe = ConfigManager._loadWokRecipe()
        return ConfigManager._wokRecipe
    
    @staticmethod
    def getData():
        '''获取数据文件'''
        if ConfigManager._data is None:
            ConfigManager._data = ConfigManager._loadData()
        return ConfigManager._data
    
    @staticmethod
    def getPrefix():
        '''获取消息前缀'''
        if ConfigManager._prefix is None:
            ConfigManager._prefix = ConfigManager.getConfig().getString("Messages.Prefix")
        return ConfigManager._prefix
    
    @staticmethod
    def reloadAll():
        '''重新加载所有配置文件'''
        ConfigManager._config = ConfigManager._loadConfig()
        ConfigManager._choppingBoardRecipe = ConfigManager._loadChoppingBoardRecipe()
        ConfigManager._wokRecipe = ConfigManager._loadWokRecipe()
        ConfigManager._data = ConfigManager._loadData()

# 修改全局变量赋值
Config = ConfigManager.getConfig()
Prefix = ConfigManager.getConfig().getString("Messages.Prefix")
ChoppingBoardRecipe = ConfigManager.getChoppingBoardRecipe()
WokRecipe = ConfigManager.getWokRecipe()
Data = ConfigManager.getData()
Console = Bukkit.getServer().getConsoleSender()

CraftEngineAvailable = False
MMOItemsAvailable = False

def ServerPluginLoad():
    '''
    在插件加载时检查CraftEngine和MMOItems插件是否可用，并注册相关事件监听器
    '''
    global CraftEngineAvailable, MMOItemsAvailable
    CraftEngineAvailable = Bukkit.getPluginManager().isPluginEnabled("CraftEngine")
    if CraftEngineAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.CraftEngine"), {"Prefix": Prefix})
        from net.momirealms.craftengine.bukkit.api.event import (  # type: ignore
            CustomBlockInteractEvent,
            CustomBlockBreakEvent,
        )
        ps.listener.registerListener(InteractionCraftEngineBlock, CustomBlockInteractEvent)
        ps.listener.registerListener(BreakCraftEngineBlock, CustomBlockBreakEvent)
    MMOItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("MMOItems")
    if MMOItemsAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.MMOItems"), {"Prefix": Prefix})

def InteractionVanillaBlock(E):
    '''处理玩家与原版方块的交互事件

    参数
        E: PlayerInteractEvent事件对象
    '''
    ClickBlock = E.getClickedBlock()
    if ClickBlock is None: return
    if E.getHand() != EquipmentSlot.HAND: return
    ClickPlayer = E.getPlayer()
    ClickBlockType = ClickBlock.getType().name()
    FileKey = GetFileKey(ClickBlock)
    # 判断点击的方块是否为砧板
    if not Config.getBoolean("Setting.ChoppingBoard.Custom"):
        if ClickBlockType == Config.getString("Setting.ChoppingBoard.Material"):
            if E.getAction() != Action.LEFT_CLICK_BLOCK: return
            if Config.getBoolean("Setting.ChoppingBoard.StealthInteraction"):
                if not ClickPlayer.isSneaking(): return
            else:
                if ClickPlayer.isSneaking(): return
            if not Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
                if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR: return
            E.setCancelled(True)
            HasExistingDisplay = Data.contains("ChoppingBoard." + FileKey)
            InteractionChoppingBoard(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return
    # 判断点击的方块是否为炒锅
    if not Config.getBoolean("Setting.Wok.Custom"):
        if ClickBlockType == Config.getString("Setting.Wok.Material"):
            BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
            BottomBlockType = BottomBlock.getType().name()
            HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
            HeatLevel = None
            if CraftEngineAvailable:
                try:
                    from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
                    if CraftEngineBlocks.isCustomBlock(BottomBlock):
                        BottomBlockState = CraftEngineBlocks.getCustomBlockState(BottomBlock)
                        CraftEngineKey = "craftengine " + str(BottomBlockState)
                        if CraftEngineKey in HeatControl:
                            HeatLevel = Config.getString("Setting.Wok.HeatControl." + CraftEngineKey)
                except: pass
            if HeatLevel is None and BottomBlockType in HeatControl:
                HeatLevel = Config.getString("Setting.Wok.HeatControl." + BottomBlockType)
            if HeatLevel is None: return
            if E.getAction() == Action.RIGHT_CLICK_BLOCK:
                if Config.getBoolean("Setting.Wok.StealthInteraction"):
                    if not ClickPlayer.isSneaking(): return
                else:
                    if ClickPlayer.isSneaking(): return
                MainHandItem = ClickPlayer.getInventory().getItemInMainHand()  
                if not ToolUtils.isToolItem(MainHandItem, Config, "Wok",  "Spatula"): return
                FileKey = GetFileKey(ClickBlock)
                HasExistingDisplay = Data.get("Wok")
                if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
                else: HasExistingDisplay = False
                if HasExistingDisplay:
                    E.setCancelled(True)
                    OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel)
                else:
                    E.setCancelled(True)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                return
            if E.getAction() != Action.LEFT_CLICK_BLOCK: return
            FileKey = GetFileKey(ClickBlock)
            HasExistingDisplay = Data.get("Wok")
            if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
            else: HasExistingDisplay = False
            if Config.getBoolean("Setting.Wok.StealthInteraction"):
                if not ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(Data, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel)
                        return
                    return
            else:
                if ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(Data, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel)
                        return
                    return
            E.setCancelled(True)
            InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay, HeatLevel)
            return

def InteractionCraftEngineBlock(E):
    '''处理CraftEngine方块的交互事件

    参数
        E: BlockInteractEvent事件对象
    '''
    from net.momirealms.craftengine.core.entity.player import InteractionHand  # type: ignore
    from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
    if E.hand() != InteractionHand.MAIN_HAND: return
    ClickPlayer = E.player()
    ClickBlock = E.bukkitBlock()
    if ClickBlock is None: return
    FileKey = GetFileKey(ClickBlock)
    # 判断CraftEngine方块是否为砧板
    if Config.getBoolean("Setting.ChoppingBoard.Custom"):
        Identifier, ID = Config.getString("Setting.ChoppingBoard.Material").split(" ", 1)
        if Identifier != "craftengine":
            return
        ClickBlockState = CraftEngineBlocks.getCustomBlockState(ClickBlock)
        if str(ClickBlockState) == ID:
            if E.action() != E.Action.LEFT_CLICK: return
            if Config.getBoolean("Setting.ChoppingBoard.StealthInteraction"):
                if not ClickPlayer.isSneaking(): return
            else:
                if ClickPlayer.isSneaking(): return
            if not Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
                if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR: return
            E.setCancelled(True)
            HasExistingDisplay = Data.contains("ChoppingBoard." + FileKey)
            InteractionChoppingBoard(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return
    # 判断CraftEngine方块是否为炒锅
    if Config.getBoolean("Setting.Wok.Custom"):
        Identifier, ID = Config.getString("Setting.Wok.Material").split(" ", 1)
        if Identifier != "craftengine": return
        ClickBlockState = CraftEngineBlocks.getCustomBlockState(ClickBlock)
        if str(ClickBlockState) == ID:
            BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
            HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
            HeatLevel = None
            if CraftEngineBlocks.isCustomBlock(BottomBlock):
                BottomBlockState = CraftEngineBlocks.getCustomBlockState(BottomBlock)
                CraftEngineKey = "craftengine " + str(BottomBlockState)
                if CraftEngineKey in HeatControl:
                    HeatLevel = Config.getString("Setting.Wok.HeatControl." + CraftEngineKey)
            if HeatLevel is None:
                BottomBlockType = BottomBlock.getType().name()
                if BottomBlockType in HeatControl:
                    HeatLevel = Config.getString("Setting.Wok.HeatControl." + BottomBlockType)
            if HeatLevel is None: return
            if E.action() == E.Action.RIGHT_CLICK:
                if Config.getBoolean("Setting.Wok.StealthInteraction"):
                    if not ClickPlayer.isSneaking(): return
                else:
                    if ClickPlayer.isSneaking(): return
                MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
                if not ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula"): return
                FileKey = GetFileKey(ClickBlock)
                HasExistingDisplay = Data.get("Wok")
                if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
                else: HasExistingDisplay = False
                if HasExistingDisplay:
                    E.setCancelled(True)
                    OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel)
                else:
                    E.setCancelled(True)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                return
            if E.action() != E.Action.LEFT_CLICK: return
            E.setCancelled(True)
            FileKey = GetFileKey(ClickBlock)
            HasExistingDisplay = Data.get("Wok")
            if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
            else: HasExistingDisplay = False
            if Config.getBoolean("Setting.Wok.StealthInteraction"):
                if not ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(Data, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel)
                        return
                    return
            else:
                if ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(Data, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel)
                        return
                    return
            InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay, HeatLevel)
            return

def BreakVanillaBlock(E):
    '''处理砧板方块被破坏的事件

    参数
        E: BlockBreakEvent事件对象
    '''
    Block = E.getBlock()
    FileKey = GetFileKey(Block)
    # 处理砧板方块
    ChoppingBoard = Config.getBoolean("Setting.ChoppingBoard.Custom")
    if not ChoppingBoard:
        try:
            MaterialSetting = Config.getString("Setting.ChoppingBoard.Material")
            if Block.getType() == Material.valueOf(MaterialSetting):
                HasExistingDisplay = Data.contains("ChoppingBoard." + FileKey)
                if HasExistingDisplay:
                    DisplayLocation = CalculateDisplayLocation(Block, Config, "ChoppingBoard")
                    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
                    if ItemDisplayEntity:
                        DisplayItem = ItemDisplayEntity.getItemStack()
                        if DisplayItem:
                            ItemEntity = Block.getWorld().dropItem(ItemDisplayEntity.getLocation(), DisplayItem)
                            ItemEntity.setPickupDelay(0)
                        ItemDisplayEntity.remove()
                    Data.set("ChoppingBoard." + FileKey, None)
                    Data.save()
                return
        except: 
            pass
    # 处理炒锅方块
    Wok = Config.getBoolean("Setting.Wok.Custom")
    if not Wok:
        try:
            MaterialSetting = Config.getString("Setting.Wok.Material")
            if Block.getType() == Material.valueOf(MaterialSetting):
                HasExistingDisplay = Data.contains("Wok." + FileKey)
                if HasExistingDisplay:
                    DisplayLocation = CalculateDisplayLocation(Block.getLocation(), Config, "Wok")
                    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                    if NearbyDisplays:
                        for Display in NearbyDisplays:
                            if Display and not Display.isDead():
                                DisplayItem = Display.getItemStack()
                                if DisplayItem:
                                    ItemEntity = Block.getWorld().dropItem(Display.getLocation(), DisplayItem)
                                    ItemEntity.setPickupDelay(0)
                                Display.remove()
                    Data.set("Wok." + FileKey, None)
                    Data.save()
                return
        except:
            pass

def BreakCraftEngineBlock(E):
    '''处理CraftEngine方块被破坏的事件

    参数
        E: CustomBlockBreakEvent事件对象
    '''
    BreakBlock = E.bukkitBlock()
    if BreakBlock is None:  return
    FileKey = GetFileKey(BreakBlock)
    # 处理砧板方块
    if Config.getBoolean("Setting.ChoppingBoard.Custom"):
        MaterialSetting = Config.getString("Setting.ChoppingBoard.Material")
        if " " in MaterialSetting:
            Identifier, ID = MaterialSetting.split(" ", 1)
            if Identifier == "craftengine":
                try:
                    from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
                    ClickBlockState = CraftEngineBlocks.getCustomBlockState(BreakBlock)
                    if ClickBlockState is not None and str(ClickBlockState) == ID:
                        HasExistingDisplay = Data.contains("ChoppingBoard." + FileKey)
                        if HasExistingDisplay:
                            DisplayLocation = CalculateDisplayLocation(BreakBlock, Config, "ChoppingBoard")
                            ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
                            if ItemDisplayEntity:
                                DisplayItem = ItemDisplayEntity.getItemStack()
                                if DisplayItem:
                                    ItemEntity = BreakBlock \
                                        .getWorld() \
                                        .dropItem(ItemDisplayEntity.getLocation(), DisplayItem)
                                    ItemEntity.setPickupDelay(0)
                                ItemDisplayEntity.remove()
                            Data.set("ChoppingBoard." + FileKey, None)
                            Data.save()
                        return
                except: pass
    # 处理炒锅方块
    if Config.getBoolean("Setting.Wok.Custom"):
        MaterialSetting = Config.getString("Setting.Wok.Material")
        if " " in MaterialSetting:
            Identifier, ID = MaterialSetting.split(" ", 1)
            if Identifier == "craftengine":
                try:
                    from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
                    ClickBlockState = CraftEngineBlocks.getCustomBlockState(BreakBlock)
                    if ClickBlockState is not None and str(ClickBlockState) == ID:
                        HasExistingDisplay = Data.contains("Wok." + FileKey)
                        if HasExistingDisplay:
                            DisplayLocation = CalculateDisplayLocation(BreakBlock.getLocation(), Config, "Wok")
                            NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                            if NearbyDisplays:
                                for Display in NearbyDisplays:
                                    if Display and not Display.isDead():
                                        DisplayItem = Display.getItemStack()
                                        if DisplayItem:
                                            ItemEntity = BreakBlock.getWorld().dropItem(Display.getLocation(),
                                                                                        DisplayItem)
                                            ItemEntity.setPickupDelay(0)
                                        Display.remove()
                            Data.set("Wok." + FileKey, None)
                            Data.save()
                        return
                except: pass

def InteractionChoppingBoard(ClickPlayer, Block, Config, FileKey, HasExistingDisplay):
    '''交互砧板
    
    参数
        ClickPlayer: 点击玩家
        Block: 点击的方块
        Config: 配置对象
        FileKey: 数据文件键
        HasExistingDisplay: 是否存在已存在的展示实体
    '''
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if HasExistingDisplay:
            if ToolUtils.isToolItem(MainHandItem, Config, "ChoppingBoard", "KitchenKnife"):
                BlockLoc = Block.getLocation()
                HandleCutting(ClickPlayer,BlockLoc.getWorld(),BlockLoc.getX(),BlockLoc.getY(),BlockLoc.getZ(),Config)
                return
            else:
                MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.TakeOffItem"))
                return
        else:
            DisplayItem = MainHandItem.clone()
            DisplayItem.setAmount(1)
            MainHandItem.setAmount(MainHandItem.getAmount() - 1)
            DisplayLocation = CalculateDisplayLocation(Block, Config, "ChoppingBoard")
            ItemDisplayEntity = CreateItemDisplay(DisplayLocation, DisplayItem, Config, "ChoppingBoard")
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardAddItem"))
            if not Data.contains("ChoppingBoard." + FileKey):
                Data.set("ChoppingBoard." + FileKey, 0)
                Data.save()
                return
    elif not MainHandItem or MainHandItem.getType() == Material.AIR:
        if HasExistingDisplay:
            DisplayLocation = CalculateDisplayLocation(Block, Config, "ChoppingBoard")
            ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)[0]
            if ItemDisplayEntity:
                DisplayItem = ItemDisplayEntity.getItemStack()
                if DisplayItem: ClickPlayer.getInventory().setItemInMainHand(DisplayItem.clone())
                ItemDisplayEntity.remove()
                Data.set("ChoppingBoard." + FileKey, None)
                Data.save()
                return

def HandleCutting(Player, World, X, Y, Z, Config):
    '''处理砧板上的切割操作

    参数
        Player: 执行切割的玩家
        World: 砧板所在的世界
        X: 砧板的X坐标
        Y: 砧板的Y坐标
        Z: 砧板的Z坐标
        Config: 配置对象
    '''
    BaseLocation = Location(World, X, Y, Z)
    DisplayLocation = CalculateDisplayLocation(BaseLocation, Config, "ChoppingBoard")
    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)[0]
    if not ItemDisplayEntity: return
    DisplayItem = ItemDisplayEntity.getItemStack()
    if not DisplayItem: return
    RecipeConfig = ChoppingBoardRecipe
    ItemMaterial = ToolUtils.getItemIdentifier(DisplayItem)
    RequiredCuts = RecipeConfig.getInt(ItemMaterial + ".Count")
    ResultMaterial = RecipeConfig.getString(ItemMaterial + ".Output")
    if not RequiredCuts or RequiredCuts == 0:
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.CannotCut"))
        return
    CoordKey = "{},{},{},{}".format(int(X), int(Y), int(Z), World.getName())
    FileKey = "ChoppingBoard.{}".format(CoordKey)
    CurrentCuts = Data.getInt(FileKey, 0)
    CurrentCuts += 1
    Data.set(FileKey, CurrentCuts)
    Data.save()
    particleType = Config.getString("Setting.Particle.ChoppingBoardCutItem.Type", "CLOUD")
    particleAmount = Config.getInt("Setting.Particle.ChoppingBoardCutItem.Amount")
    particleoffsetX = Config.getInt("Setting.Particle.ChoppingBoardCutItem.Xoffset")
    particleoffsetY = Config.getInt("Setting.Particle.ChoppingBoardCutItem.Yoffset")
    particleoffsetZ = Config.getInt("Setting.Particle.ChoppingBoardCutItem.Zoffset")
    particleSpeed = Config.getInt("Setting.Particle.ChoppingBoardCutItem.Speed")
    particleLocation = Location(World, X + 0.5, Y + 1.1, Z + 0.5)
    PlayParticle(
        particleLocation,
        particleType,
        particleAmount,
        particleoffsetX,
        particleoffsetY,
        particleoffsetZ,
        particleSpeed)
    if (Config.getBoolean("Setting.ChoppingBoard.Damage.Enable")
        and
        random.randint(1, 100) <= Config.getInt("Setting.ChoppingBoard.Damage.Chance")):
        DamageValue = Config.getInt("Setting.ChoppingBoard.Damage.Value")
        Player.damage(DamageValue)
        MiniMessageUtils.playSound(Player, Config.get("Setting.Sound.ChoppingBoardCutHand"))
        MiniMessageUtils.sendTitle(Player,Config.getString("Messages.Title.CutHand.MainTitle"),
                                   Config.getString("Messages.Title.CutHand.SubTitle"),
                                   {"Damage": str(DamageValue)})
    MiniMessageUtils.sendActionBar(Player,Config.getString("Messages.ActionBar.CutAmount"),
                                   {"CurrentCount": str(CurrentCuts), "NeedCount": str(RequiredCuts)})
    MiniMessageUtils.playSound(Player, Config.get("Setting.Sound.ChoppingBoardCutItem"))
    if CurrentCuts >= RequiredCuts:
        if " " in ResultMaterial: GiveItem = ResultMaterial
        else: GiveItem = RequiredCuts
        GiveAmount = RecipeConfig.getInt(ItemMaterial + ".OutputAmount")
        ResultItemStack = ToolUtils.createItemStack(GiveItem, GiveAmount)
        if not ResultItemStack:
            MiniMessageUtils.sendMessage(Console,Config.getString("Messages.InvalidMaterial"),
                                         {"Prefix": Config.getString("Messages.Prefix"), "Material": ResultMaterial})
            return
        if ResultItemStack is not None:
            ItemDisplayEntity.remove()
            DropLocation = Location(World, X + 0.5, Y + 1.0, Z + 0.5)
            if Config.getBoolean("Setting.ChoppingBoard.Drop"):
                ItemEntity = World.dropItem(DropLocation, ResultItemStack)
                ItemEntity.setPickupDelay(20)
            else: GiveItemToPlayer(Player, ResultItemStack)
            Data.set(FileKey, None)
            Data.save()
        else:
            MiniMessageUtils.sendMessage(Console,Config.getString("Messages.InvalidMaterial"),
                                         {"Prefix": Config.getString("Messages.Prefix"), "Material": ResultMaterial})
            return

def InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay, HeatLevel):
    '''处理炒锅的交互事件
    
    参数
        ClickPlayer: 玩家对象
        ClickBlock: 点击的方块对象
        Config: 配置文件对象
        FileKey: 炒锅的坐标和世界名
        HasExistingDisplay: 炒锅是否已经有显示物
        HeatLevel: 炒锅的温度等级
    '''
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula"):
            ItemList = Data.getStringList("Wok." + FileKey + ".Items")
            if not ItemList:
                MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.WokNoItem"))
                return
            LastStirTime = Data.getLong("Wok." + FileKey + ".LastStirTime", 0)
            StirCount = Data.getInt("Wok." + FileKey + ".Count", 0)
            CurrentTime = System.currentTimeMillis()
            if StirCount != 0:
                if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.BurntFood"))
                    return
            StirFriedTime = Data.getLong("Wok." + FileKey + ".StirFriedTime", 0)
            if StirFriedTime != 0:
                if CurrentTime - StirFriedTime < Config.getInt("Setting.Wok.Dalay") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer,
                                                   Config.getString("Messages.ActionBar.StirFriedTooQuickly"))
                    return
            particleType = Config.getString("Setting.Particle.WokStirItem.Type", "CAMPFIRE_COSY_SMOKE")
            particleAmount = Config.getInt("Setting.Particle.WokStirItem.Amount")
            particleoffsetX = Config.getInt("Setting.Particle.WokStirItem.Xoffset")
            particleoffsetY = Config.getInt("Setting.Particle.WokStirItem.Yoffset")
            particleoffsetZ = Config.getInt("Setting.Particle.WokStirItem.Zoffset")
            particleSpeed = Config.getInt("Setting.Particle.WokStirItem.Speed")
            particleLocation = ClickBlock.getLocation().add(0.5, 1.1, 0.5)
            PlayParticle(
                particleLocation,
                particleType,
                particleAmount,
                particleoffsetX,
                particleoffsetY,
                particleoffsetZ,
                particleSpeed)
            Data.set("Wok." + FileKey + ".StirFriedTime", System.currentTimeMillis())
            Data.set("Wok." + FileKey + ".LastStirTime", System.currentTimeMillis())
            StirCount += 1
            Data.set("Wok." + FileKey + ".Count", StirCount)
            UpdatedItemList = []
            for ItemEntry in ItemList:
                Parts = ItemEntry.split(" ")
                ItemType = Parts[0]
                ItemID = Parts[1]
                Quantity = int(Parts[2])
                StirTimes = int(Parts[3]) + 1
                UpdatedEntry = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                UpdatedItemList.append(UpdatedEntry)
            Data.set("Wok." + FileKey + ".Items", UpdatedItemList)
            Data.save()
            MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.StirCount"),
                                           {"Count": StirCount})
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokStirItem"))
            return
        BowlCustom = Config.getBoolean("Setting.Wok.NeedBowl")
        if BowlCustom and MainHandItem.getType() == Material.BOWL:
            MainHandItem.setAmount(MainHandItem.getAmount() - 1)
            GetWokOutput(Data, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel)
            return
        if HasExistingDisplay:
            CurrentItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
            ItemList = Data.getStringList("Wok." + FileKey + ".Items")
            NeedAddItem = False
            DisplayLocation = CalculateDisplayLocation(ClickBlock.getLocation(), Config, "Wok")
            NearbyDisplays = FindNearbyDisplay(DisplayLocation)
            for Index, ItemEntry in enumerate(ItemList):
                Parts = ItemEntry.split(" ")
                ItemTypeID = Parts[0] + " " + Parts[1]
                if ItemTypeID == CurrentItemIdentifier:
                    CurrentAmount = int(Parts[2]) + 1
                    StirCount = int(Parts[3])
                    ItemList[Index] = ItemTypeID + " " + str(CurrentAmount) + " " + str(StirCount)
                    NeedAddItem = True
                    for Display in NearbyDisplays:
                        if Display and not Display.isDead():
                            DisplayItem = Display.getItemStack()
                            if DisplayItem and ToolUtils.getItemIdentifier(DisplayItem) == CurrentItemIdentifier:
                                DisplayItem.setAmount(CurrentAmount)
                                Display.setItemStack(DisplayItem)
                                break
                    break
            if not NeedAddItem:
                ItemListLength = len(ItemList)
                ExtraOffset = 0.0001 * ItemListLength
                ItemList.append(CurrentItemIdentifier + " 1 0")
                DisplayItem = MainHandItem.clone()
                DisplayLocation = CalculateDisplayLocation(ClickBlock.getLocation(), Config, "Wok", ExtraOffset)
                CreateItemDisplay(DisplayLocation, DisplayItem, Config, "Wok")
            Data.set("Wok." + FileKey + ".Items", list(ItemList))
            Data.save()
            MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.WokAddItem"),
                                           {"Material": ToolUtils.getItemDisplayName(MainHandItem)})
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            return
        else:
            SaveValue = ToolUtils.getItemIdentifier(MainHandItem) + " 1 0"
            Data.set("Wok." + FileKey + ".Items", [SaveValue])
            Data.set("Wok." + FileKey + ".Count", 0)
            Data.save()
            DisplayItem = MainHandItem.clone()
            DisplayLocation = CalculateDisplayLocation(ClickBlock.getLocation(), Config, "Wok")
            CreateItemDisplay(DisplayLocation, DisplayItem, Config, "Wok")
            MiniMessageUtils.sendActionBar(ClickPlayer,Config.getString("Messages.ActionBar.WokAddItem"),
                                           {"Material": ToolUtils.getItemDisplayName(MainHandItem)})
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            return
    else:
        if Data.getInt("Wok." + FileKey + ".Count") > 0:
            if Config.getBoolean("Setting.Wok.Damage.Enable"):
                DamageValue = Config.getInt("Setting.Wok.Damage.Value")
                ClickPlayer.damage(DamageValue)
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokScald"))
                MiniMessageUtils.sendTitle(ClickPlayer,Config.getString("Messages.Title.Scald.MainTitle"),
                                           Config.getString("Messages.Title.Scald.SubTitle"),{"Damage": DamageValue})
        ItemList = Data.getStringList("Wok." + FileKey + ".Items")
        if not ItemList:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
            return
        LastItemEntry = ItemList[-1]
        Parts = LastItemEntry.split(" ")
        ItemType = Parts[0]
        ItemID = Parts[1]
        Quantity = int(Parts[2])
        StirTimes = int(Parts[3])
        Quantity -= 1
        ItemToGive = ToolUtils.createItemStack(LastItemEntry)
        if ItemToGive: GiveItemToPlayer(ClickPlayer, ItemToGive)
        if Quantity <= 0:
            ItemList.pop()
            if not ItemList: Data.set("Wok." + FileKey, None)
            else: Data.set("Wok." + FileKey + ".Items", ItemList)
            DisplayLocation = CalculateDisplayLocation(ClickBlock.getLocation(), Config, "Wok")
            NearbyDisplays = FindNearbyDisplay(DisplayLocation)
            if NearbyDisplays:
                HighestDisplay = None
                MaxY = -9999
                for display in NearbyDisplays:
                    loc = display.getLocation()
                    if loc.getY() > MaxY:
                        MaxY = loc.getY()
                        HighestDisplay = display
                if HighestDisplay: HighestDisplay.remove()
        else:
            ItemList[-1] = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
            Data.set("Wok." + FileKey + ".Items", ItemList)
        Data.save()

def OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel):
    '''输出炒锅信息
    
    参数
        ClickPlayer: 玩家对象
        Config: 配置文件对象
        FileKey: 炒锅的坐标和世界名
        HeatLevel: 炒锅的温度等级
    '''
    ItemList = Data.getStringList("Wok." + FileKey + ".Items")
    TotalCount = Data.getString("Wok." + FileKey + ".Count")
    MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokTop"))
    for Item in ItemList:
        Parts = Item.split(" ", 3)
        PluginName, ItemName, Amount, Count = Parts
        ItemStack = ToolUtils.createItemStack(Item)
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokContent"),
                                     {"ItemName": ToolUtils.getItemDisplayName(ItemStack),
                                      "ItemAmount": Amount, "Count": Count})
    MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokDown"), {"Count": TotalCount})
    MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokHeatControl"), {"Heat": HeatLevel})

def GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock, HeatLevel = 0):
    '''获取炒锅的输出
    
    参数：
        DataFile - 数据文件
        Config - 配置文件
        FileKey -  cooking_wok_data 文件的键值
        ClickPlayer - 点击的玩家
        ClickBlock - 点击的方块
        HeatLevel - 热量等级
    '''
    DataStirFryAmount = DataFile.getInt("Wok." + FileKey + ".Count")
    if DataStirFryAmount == 0: return
    ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
    if not ItemList:
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
        return
    RecipeKeys = WokRecipe.getKeys(False)
    # 遍历所有配方
    for RecipeKey in RecipeKeys:
        RecipeHeat = WokRecipe.getInt(RecipeKey + ".HeatControl", 0)
        if RecipeHeat != int(HeatLevel) or int(HeatLevel) == 0: continue
        RecipeItemList = WokRecipe.getStringList(RecipeKey + ".Item")
        if len(ItemList) != len(RecipeItemList): continue
        Match = True
        GreaterThan = 0
        LessThan = 0
        for Idx in range(len(ItemList)):
            ItemEntry = ItemList[Idx].split(" ")
            RecipeEntry = RecipeItemList[Idx].split(" ")
            if ItemEntry[0] != RecipeEntry[0] or ItemEntry[1] != RecipeEntry[1]:
                Match = False
                break
            Tolerance = WokRecipe.getInt(RecipeKey + ".FaultTolerance")
            Amount = 0
            for I in range(len(ItemList)):
                if Amount > Tolerance:
                    Match = False
                    break
                ItemEntry = ItemList[I].split(" ")
                RecipeEntry = RecipeItemList[I].split(" ")
                if ItemEntry[2] != RecipeEntry[2]:
                    Amount += abs(int(ItemEntry[2]) - int(RecipeEntry[2]))
                    continue
                RecipeStirFry = RecipeEntry[3]
                if "-" in RecipeStirFry:
                    Num1, Num2 = RecipeStirFry.split("-")
                    NumRange = range(int(Num1), int(Num2))
                    if int(ItemEntry[3]) not in NumRange:
                        if int(ItemEntry[3]) > max(NumRange):
                            GreaterThan += 1
                            Amount += 1
                            continue
                        elif int(ItemEntry[3]) < min(NumRange):
                            LessThan += 1
                            Amount += 1
                            continue
                elif int(ItemEntry[3]) != RecipeStirFry:
                    if int(ItemEntry[3]) > RecipeStirFry:
                        GreaterThan += 1
                        Amount += 1
                        continue
                    elif int(ItemEntry[3]) < RecipeStirFry:
                        LessThan += 1
                        Amount += 1
                        continue
                continue
        if Match:
            StirFryAmount = WokRecipe.get(RecipeKey + ".Count")
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokTakeOffItem"))
            if "-" in StirFryAmount:
                MaxValue, MinValue = StirFryAmount.split("-")
                RandRange = range(int(MaxValue), int(MinValue))
                MaxValue = max(RandRange)
                MinValue = min(RandRange)
            else:
                MaxValue = WokRecipe.getInt(RecipeKey + ".Count")
                MinValue = WokRecipe.getInt(RecipeKey + ".Count")
            LastStirTime = DataFile.getLong("Wok." + FileKey + ".LastStirTime", 0)
            CurrentTime = System.currentTimeMillis()
            if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                RawItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            if DataStirFryAmount > MaxValue:
                BurntItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            elif DataStirFryAmount < MinValue:
                RawItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            if Config.getBoolean("Setting.Wok.Failure.Enable"):
                Chance = Config.getInt("Setting.Wok.Failure.Chance")
                if random.randint(1, 100) < Chance:
                    ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
                    OutputWokItem(RecipeKey,ErrorRecipe,WokRecipe,ClickPlayer,DataFile,FileKey,ClickBlock,Config)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.FailureRecipe"))
                    return
            if Amount <= Tolerance:
                OutputWokItem(RecipeKey, RecipeKey, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.SuccessRecipe"))
                return
            elif GreaterThan > LessThan:
                BurntItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            elif LessThan > GreaterThan:
                RawItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
        else: continue
    if Config.getBoolean("Setting.Wok.Failure.Enable"):
        ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
        OutputWokItem(RecipeKey, ErrorRecipe, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ErrorRecipe"))

def OutputWokItem(RecipeKey, Item, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config):
    '''输出炒锅物品，并清除展示实体与数据
    
    参数
        RecipeKey: 配方Key
        Item: 输出物品
        RecipeConfig: 配方配置文件
        ClickPlayer: 点击玩家
        DataFile: 玩家数据文件
        FileKey: 玩家数据文件Key
        ClickBlock: 点击方块
        Config: 配置文件
    '''
    if " " not in Item:
        GiveAmount = RecipeConfig.getInt(RecipeKey + ".Amount")
        ITEM = ToolUtils.createItemStack(Item)
        ITEM.setAmount(GiveAmount)
    else:
        try:
            Parts = Item.split(" ", 2)
            ITEM = ToolUtils.createItemStack(Item)
            ITEM.setAmount(int(Parts[2]))
        except: return
    if Config.getBoolean("Setting.Wok.Drop"):
        DropLocation = ClickBlock.getLocation().add(0.5, 1.0, 0.5)
        ItemEntity = ClickBlock.getWorld().dropItem(DropLocation, ITEM)
        ItemEntity.setPickupDelay(20)
    else: GiveItemToPlayer(ClickPlayer, ITEM)
    DataFile.set("Wok." + FileKey, None)
    DataFile.save()
    DisplayLocation = CalculateDisplayLocation(ClickBlock.getLocation(), Config, "Wok")
    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
    if NearbyDisplays:
        for display in NearbyDisplays: display.remove()

class ToolUtils:
    '''工具类'''
    
    # 类常量
    CRAFTENGINE = "craftengine"
    MMOITEMS = "mmoitems"
    MINECRAFT = "minecraft"
    
    @staticmethod
    def isToolItem(Item, Config, Type, Tool):
        '''判断物品是否为指定的工具类型
        
        参数:
            Item: 物品对象
            Config: 配置对象
            Type: 工具类型
            Tool: 工具名称
        返回:
            bool: 是否为指定工具
        '''
        if not Item or Item.getType() == Material.AIR:
            return False
        CustomSetting = Config.getBoolean("Setting." + Type + "." + Tool + ".Custom")
        MaterialSetting = Config.getString("Setting." + Type + "." + Tool + ".Material")
        if CustomSetting:
            if ' ' in MaterialSetting:
                Identifier, ID = MaterialSetting.split(' ', 1)
                if Identifier == ToolUtils.CRAFTENGINE and CraftEngineAvailable:
                    return ToolUtils.isCraftEngineItem(Item, ID)
                elif Identifier == ToolUtils.MMOITEMS and MMOItemsAvailable:
                    return ToolUtils.isMMOItemsItem(Item, ID)
        else:
            try: return Item.getType() == Material.valueOf(MaterialSetting)
            except: pass
        return False

    @staticmethod
    def isCraftEngineItem(Item, ExpectedID):
        '''检查是否为指定ID的CraftEngine物品'''
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            if CraftEngineItems.isCustomItem(Item):
                ItemId = CraftEngineItems.getCustomItemId(Item)
                return str(ItemId) == ExpectedID
        except Exception: return False

    @staticmethod
    def isMMOItemsItem(Item, ExpectedID):
        '''检查是否为指定ID的MMOItems物品'''
        try:
            from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                CombinedId = str(ItemType) + ":" + str(ItemId)
                return CombinedId == ExpectedID
        except Exception: return False

    @staticmethod
    def getItemIdentifier(Item):
        '''获取物品的唯一标识符字符串
        
        参数:
            Item: 物品对象
        
        返回:
            标识符字符串 (格式: "类型 标识符")
        '''
        # 检查CraftEngine物品
        if CraftEngineAvailable:
            craftEngineId = ToolUtils.getCraftEngineItemId(Item)
            if craftEngineId:
                return ToolUtils.CRAFTENGINE + " " + str(craftEngineId)
        # 检查MMOItems物品
        if MMOItemsAvailable:
            mmoItemsId = ToolUtils.getMMOItemsItemId(Item)
            if mmoItemsId:
                return ToolUtils.MMOITEMS + " " + mmoItemsId
        # 默认返回原版物品标识
        return ToolUtils.MINECRAFT + " " + Item.getType().name()

    @staticmethod
    def getCraftEngineItemId(Item):
        '''获取CraftEngine物品ID'''
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            if CraftEngineItems.isCustomItem(Item):
                return CraftEngineItems.getCustomItemId(Item)
        except Exception: return None

    @staticmethod
    def getMMOItemsItemId(Item):
        '''获取MMOItems物品ID'''
        try:
            from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                return str(ItemType) + ":" + str(ItemId)
        except Exception: return None

    @staticmethod
    def createItemStack(ItemKey, Amount=1):
        '''创建物品栈
        
        参数:
            ItemKey: 物品键
            Amount: 数量
        
        返回:
            ItemStack: 物品栈
        '''
        if not ItemKey: return None
        Parts = ItemKey.split(" ")
        if len(Parts) < 1: return None
        if len(Parts) < 3: Amount = Amount
        else: Amount = int(Parts[2])
        ItemType = Parts[0]
        
        # 根据物品类型创建不同的物品栈
        if ItemType == ToolUtils.MINECRAFT:
            return ToolUtils.createMinecraftItem(Parts, Amount)
        elif ItemType == ToolUtils.CRAFTENGINE and CraftEngineAvailable:
            return ToolUtils.createCraftEngineItem(Parts, Amount)
        elif ItemType == ToolUtils.MMOITEMS and MMOItemsAvailable:
            return ToolUtils.createMMOItemsItem(Parts, Amount)
        else:
            # 尝试将整个ItemKey作为原版物品名
            try:
                Item = Material.valueOf(ItemType)
                return ItemStack(Item, Amount)
            except:
                return None

    @staticmethod
    def createMinecraftItem(Parts, Amount):
        '''创建原版Minecraft物品'''
        try:
            if len(Parts) > 1: Item = Material.valueOf(Parts[1])
            else: Item = Material.valueOf(Parts[0])
            return ItemStack(Item, Amount)
        except: return None

    @staticmethod
    def createCraftEngineItem(Parts, Amount):
        '''创建CraftEngine物品'''
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            from net.momirealms.craftengine.core.util import Key  # type: ignore
            if len(Parts) > 1:
                KeyParts = Parts[1].split(":")
                if len(KeyParts) >= 2:
                    CraftEngineItem = CraftEngineItems.byId(Key(KeyParts[0], KeyParts[1])).buildItemStack()
                    CraftEngineItem.setAmount(Amount)
                    return CraftEngineItem
        except Exception: return None

    @staticmethod
    def createMMOItemsItem(Parts, Amount):
        '''创建MMOItems物品'''
        try:
            from net.Indyuce.mmoitems import MMOItems  # type: ignore
            if len(Parts) > 1:
                IdParts = Parts[1].split(":")
                if len(IdParts) >= 2:
                    MMOItemsItem = MMOItems.plugin.getMMOItem(
                        MMOItems.plugin.getTypes().get(IdParts[0]), 
                        IdParts[1]
                    ).newBuilder().build()
                    MMOItemsItem.setAmount(Amount)
                    return MMOItemsItem
        except Exception: return None

    @staticmethod
    def getItemDisplayName(Item):
        '''获取物品的显示名称
        
        参数:
            Item: 物品对象
        返回:
            Obj: 显示名称字符串或组件
        '''
        # 检查CraftEngine物品
        if CraftEngineAvailable:
            try:
                from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
                from net.momirealms.craftengine.bukkit.item import BukkitItemManager  # type: ignore
                if CraftEngineItems.isCustomItem(Item):
                    return BukkitItemManager.instance().wrap(Item).hoverNameJson().get()
            except Exception: pass
        # 检查MMOItems物品
        if MMOItemsAvailable:
            try:
                from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
                NbtItem = NBTItem.get(Item)
                if NbtItem.hasType():
                    return NbtItem.getString("MMOITEMS_NAME")
            except Exception: pass
        # 默认返回原版物品名称
        return Component.translatable(Item.translationKey())

def GiveItemToPlayer(Player, Item):
    '''给予玩家物品，处理背包空间不足的情况

    参数
        Player: 目标玩家
        Item: 要给予的物品
    '''
    if Player.getInventory().firstEmpty() != -1: Player.getInventory().addItem(Item)
    else: Player.getWorld().dropItemNaturally(Player.getLocation(), Item)

def RemoveItemToPlayer(Player, Item):
    '''移除玩家物品
    参数
        Player: 玩家
        Item: 要移除的物品
    '''
    if Item.getAmount() > 1:
        Item.setAmount(Item.getAmount() - 1)
        Player.getInventory().setItemInMainHand(Item)
    else: Player.getInventory().setItemInMainHand(None)

def CreateItemDisplay(Location, Item, Config, Target):
    '''创建物品展示实体并设置属性

    参数
        Location: 生成位置
        Item: 展示的物品
        Config: 配置对象
        Target: 配方目标
    返回
        创建的展示实体
    '''
    ItemDisplayEntity = Location.getWorld().spawn(Location, ItemDisplay)
    DisplayItem = Item.clone()
    DisplayItem.setAmount(1)
    ItemDisplayEntity.setItemStack(Item)
    Scale = Config.getDouble("Setting." + Target + ".DisplayEntity.Scale")
    ScaleVector = Vector3f(Scale, Scale, Scale)
    RotX = Config.getDouble("Setting." + Target + ".DisplayEntity.Rotation.X", 0.0)
    RotY = Config.getDouble("Setting." + Target + ".DisplayEntity.Rotation.Y", 0.0)
    RotZConfig = Config.get("Setting." + Target + ".DisplayEntity.Rotation.Z")
    RotZ = 0.0
    if isinstance(RotZConfig, basestring):  # type: ignore
        if "-" in RotZConfig:
            try:
                MinValue, MaxValue = map(float, RotZConfig.split("-"))
                RotZ = random.uniform(MinValue, MaxValue)
            except ValueError: RotZ = 0.0
        else:
            try: RotZ = float(RotZConfig)
            except ValueError: RotZ = 0.0
    else:
        try: RotZ = float(RotZConfig)
        except ValueError: RotZ = 0.0
    RadX = math.radians(RotX)
    RadY = math.radians(RotY)
    RadZ = math.radians(RotZ)
    Rotation = Quaternionf().rotationXYZ(RadX, RadY, RadZ)
    New_Transform = Transformation(
        Vector3f(),
        Rotation,
        ScaleVector,
        Quaternionf())
    ItemDisplayEntity.setTransformation(New_Transform)
    ItemDisplayEntity.setInvulnerable(True)
    ItemDisplayEntity.setSilent(True)
    ItemDisplayEntity.setPersistent(True)
    ItemDisplayEntity.setGravity(False)
    ItemDisplayEntity.setCustomNameVisible(False)
    return ItemDisplayEntity

def FindNearbyDisplay(Location):
    '''在指定位置附近查找物品展示实体

    参数
        Location: 查找位置
    返回
        找到的物品展示实体或None
    '''
    FoundEntities = []
    for entity in Location.getWorld().getNearbyEntities(Location, 0.25, 0.25, 0.25):
        if entity.getType() == EntityType.ITEM_DISPLAY: FoundEntities.append(entity)
    return FoundEntities if FoundEntities else None

def GetFileKey(Block):
    '''获取砧板的数据文件键

    参数
        Block: 砧板方块
    返回
        数据文件键
    '''
    return "{},{},{},{}".format(Block.getX(), Block.getY(), Block.getZ(), Block.getWorld().getName())

def CalculateDisplayLocation(BaseLocation, Config, Target, ExtraOffset = 0):
    '''计算物品展示实体的位置

    参数
        BaseLocation: 基础位置
        Config: 配置对象
        Target: 配方目标
        ExtraOffset: 额外偏移量
    返回
        展示实体的位置
    '''
    Offset_X = Config.getDouble("Setting." + Target + ".DisplayEntity.Offset.X")
    Offset_Y = Config.getDouble("Setting." + Target + ".DisplayEntity.Offset.Y")
    Offset_Z = Config.getDouble("Setting." + Target + ".DisplayEntity.Offset.Z")
    return Location(
        BaseLocation.getWorld(),
        BaseLocation.getX() + Offset_X,
        BaseLocation.getY() + Offset_Y + ExtraOffset,
        BaseLocation.getZ() + Offset_Z)

def PlayParticle(location, particleType, count=5, offsetX=0.2, offsetY=0.2, offsetZ=0.2, speed=0.1, force=True):
    '''播放粒子效果
    
    参数:
        location: 粒子生成的位置 (Location对象)
        particleType: 粒子类型 (字符串或Particle枚举)
        count: 粒子数量 (默认5)
        offsetX: X轴偏移范围 (默认0.2)
        offsetY: Y轴偏移范围 (默认0.2)
        offsetZ: Z轴偏移范围 (默认0.2)
        speed: 粒子速度 (默认0.1)
        force: 是否强制显示给远处玩家 (默认True)
    '''
    try:
        # 如果particleType是字符串，尝试转换为Particle枚举
        if isinstance(particleType, basestring):  # type: ignore
            try: particleType = Particle.valueOf(particleType.upper())
            except: particleType = Particle.CLOUD
        
        # 播放粒子效果
        location.getWorld().spawnParticle(
            particleType,
            location,
            count,
            offsetX,
            offsetY,
            offsetZ,
            speed,
            None,  # 额外的粒子数据，默认为None
            force
        )
    except Exception as e:
        pass

ps.listener.registerListener(InteractionVanillaBlock, PlayerInteractEvent)
ps.listener.registerListener(BreakVanillaBlock, BlockBreakEvent)

def CommandExecute(sender, label, args):
    '''处理/JiuWu's Kitchen命令

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        命令执行结果
    '''
    if len(args) == 0: return False
    if args[0] == "reload":
        if isinstance(sender, Player):
            if not sender.hasPermission("jiuwukitchen.command.reload"):
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"),{"Prefix": Prefix})
                return False
        ReloadPlugin(sender)
        MiniMessageUtils.sendMessage(sender, Config.getString("Messages.Reload.LoadPlugin"), {"Prefix": Prefix})
        return True
    if isinstance(sender, Player):
        if args[0] == "clear":
            if sender.hasPermission("jiuwukitchen.command.clear"):
                for Entity in sender.getWorld().getNearbyEntities(sender.getLocation(), 0.5, 0.5, 0.5):
                    if Entity.getType() == EntityType.ITEM_DISPLAY:
                        Entity.remove()
                        return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        if args[0] == "hand":
            if sender.hasPermission("jiuwukitchen.command.hand"):
                HandItem = sender.getInventory().getItemInMainHand()
                if HandItem.getType() == Material.AIR:
                    MiniMessageUtils.sendMessage(sender, u"&7你手上没有物品")
                    return True
                ItemDisplay = HandItem.displayName()
                ItemDisplay.hoverEvent(HandItem.asHoverEvent())
                MiniMessageUtils.sendMessage(sender, ItemDisplay)
                return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        return False
    return False

def ReloadPlugin(Target = Console):
    ConfigManager.reloadAll()
    ChoppingBoardRecipeAmount = ChoppingBoardRecipe.getKeys(False).size()
    WokRecipeAmount = WokRecipe.getKeys(False).size()
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadChoppingBoardRecipe"),
                                 {"Prefix": Prefix, "Amount": int(ChoppingBoardRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadWokRecipe"),
                                 {"Prefix": Prefix, "Amount": int(WokRecipeAmount)})

def Tab_CommandExecute(sender, label, args):
    '''提供命令的补全建议

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        补全建议列表
    '''
    if isinstance(sender, Player):
        return ["reload", "clear", "hand"]
    return ["reload"]

ps.command.registerCommand(CommandExecute, Tab_CommandExecute, "jiuwukitchen", ["jk"], "")

class MiniMessageUtils:
    '''MiniMessage工具类'''

    # 类变量，存储共享资源
    MiniMessages = MiniMessage.miniMessage()
    GsonSerializer = GsonComponentSerializer.gson()
    PlainTextSerializer = PlainTextComponentSerializer.plainText()
    
    # 创建 LegacyComponentSerializer 实例
    LegacySerializer = LegacyComponentSerializer.builder().hexColors().hexCharacter('#').character('&').build()

    @staticmethod
    def isString(MessageObj):
        '''判断消息是否为字符串

        参数:
            MessageObj: 要检查的消息

        返回:
            bool: 是否为字符串
        '''
        return isinstance(MessageObj, basestring)  # type: ignore

    @staticmethod
    def containsLegacyColors(TextStr):
        '''检查文本是否包含传统颜色格式

        参数:
            TextStr: 要检查的文本

        返回:
            bool: 是否包含传统颜色格式
        '''
        if not MiniMessageUtils.isString(TextStr):
            return False

        return '&' in TextStr and re.search(r'&[0-9a-fk-orA-FK-OR]', TextStr) is not None

    @staticmethod
    def convertLegacyToMiniMessage(TextStr):
        '''将传统颜色代码转换为MiniMessage格式

        参数:
            TextStr: 包含传统颜色代码的文本

        返回:
            str: 转换后的MiniMessage格式文本
        '''
        if not MiniMessageUtils.isString(TextStr) or not MiniMessageUtils.containsLegacyColors(TextStr):
            return TextStr
        # 使用 LegacyComponentSerializer 将传统颜色代码转换为组件
        ComponentObj = MiniMessageUtils.LegacySerializer.deserialize(TextStr)
        # 将组件序列化为 MiniMessage 格式
        return MiniMessageUtils.MiniMessages.serialize(ComponentObj)

    @staticmethod
    def stringToComponent(TextStr):
        '''将字符串转换为组件

        参数:
            TextStr: 要转换的文本

        返回:
            Component: 转换后的组件
        '''
        if not MiniMessageUtils.isString(TextStr):
            return Component.empty()
        # 先转换传统颜色代码
        TextStr = MiniMessageUtils.convertLegacyToMiniMessage(TextStr)
        # 使用MiniMessage解析为组件
        return MiniMessageUtils.MiniMessages.deserialize(TextStr)

    @staticmethod
    def jsonToComponent(JsonStr):
        '''将JSON字符串转换为组件

        参数:
            JsonStr: JSON格式的字符串

        返回:
            Component: 转换后的组件
        '''
        if not MiniMessageUtils.isString(JsonStr):
            return Component.empty()
        try:
            return MiniMessageUtils.GsonSerializer.deserialize(JsonStr)
        except Exception as e:
            return MiniMessageUtils.MiniMessages.deserialize(u"<red>JSON解析错误: " + str(e) + "</red>")

    @staticmethod
    def nbtToComponent(NbtStr):
        '''将NBT字符串转换为组件

        参数:
            NbtStr: NBT格式的字符串

        返回:
            Component: 转换后的组件
        '''
        if not MiniMessageUtils.isString(NbtStr):
            return Component.empty()

        try:
            return MiniMessageUtils.jsonToComponent(NbtStr)
        except:
            return MiniMessageUtils.stringToComponent(NbtStr)

    @staticmethod
    def replaceTextPlaceholders(TextStr, PlaceholdersDict):
        '''替换字符串中的文本占位符

        参数:
            TextStr: 原始文本
            PlaceholdersDict: 占位符字典，如 {'Target': 'Notch'}
        返回:
            str: 替换后的文本
        '''
        if not MiniMessageUtils.isString(TextStr) or not isinstance(PlaceholdersDict, dict):
            return TextStr

        # 使用format方法进行替换(更高效)
        try:
            # 首先尝试使用format方法
            return TextStr.format(**PlaceholdersDict)
        except:
            # 如果format失败，使用replace方法
            for Placeholder, Replacement in PlaceholdersDict.iteritems():
                PlaceholderPattern = "{" + Placeholder + "}"
                TextStr = TextStr.replace(PlaceholderPattern, str(Replacement))

        return TextStr

    @staticmethod
    def replaceComponentPlaceholders(ComponentObj, PlaceholdersDict):
        '''解析组件中的字符占位符 (使用更高效的组件替换方法)

        参数:
            ComponentObj: 原始组件
            PlaceholdersDict: 占位符字典

        返回:
            Component: 替换后的组件
        '''
        if ComponentObj is None or not isinstance(PlaceholdersDict, dict):
            return ComponentObj
        for Placeholder, Replacement in PlaceholdersDict.iteritems():
            ReplacementComp = MiniMessageUtils.processMessage(Replacement, None)
            Config = TextReplacementConfig \
                .builder() \
                .matchLiteral("{" + Placeholder + "}") \
                .replacement(ReplacementComp) \
                .build()
            ComponentObj = ComponentObj.replaceText(Config)

        return ComponentObj

    @staticmethod
    def processMessage(MessageObj, PlaceholdersDict=None):
        '''处理消息，根据类型转换为组件并替换占位符

        参数:
            MessageObj: 原始消息
            PlaceholdersDict: 占位符字典

        返回:
            Component: 处理后的组件
        '''
        if MessageObj is None:
            return Component.empty()
        TextComp = None
        if MiniMessageUtils.isString(MessageObj):
            if MessageObj.strip().startswith('{') and MessageObj.strip().endswith('}'):
                try:
                    json.loads(MessageObj)
                    TextComp = MiniMessageUtils.jsonToComponent(MessageObj)
                except:
                    TextComp = MiniMessageUtils.stringToComponent(MessageObj)
            else:
                TextComp = MiniMessageUtils.stringToComponent(MessageObj)
        elif isinstance(MessageObj, Component):
            TextComp = MessageObj
        else:
            TextComp = MiniMessageUtils.stringToComponent(str(MessageObj))
        if PlaceholdersDict:
            TextComp = MiniMessageUtils.replaceComponentPlaceholders(TextComp, PlaceholdersDict)
        return TextComp

    @staticmethod
    def sendMessage(Target, MessageObj, PlaceholdersDict=None):
        '''给玩家发送消息

        参数:
            Target: 目标玩家
            MessageObj: 消息内容(可以是字符串、组件或JSON)
            PlaceholdersDict: 可选的占位符字典
        '''
        if MessageObj is None:
            return

        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendMessage(Comp)

    @staticmethod
    def sendTitle(Target, TitleStr, SubtitleStr, PlaceholdersDict=None, FadeIn=10, Stay=70, FadeOut=20):
        '''给玩家发送标题

        参数:
            Target: 目标玩家
            TitleStr: 标题内容
            SubtitleStr: 副标题内容
            PlaceholdersDict: 可选的占位符字典
            FadeIn: 淡入时间(ticks)
            Stay: 停留时间(ticks)
            FadeOut: 淡出时间(ticks)
        '''
        if not isinstance(Target, Player):
            return

        TitleComp = MiniMessageUtils.processMessage(
            TitleStr, PlaceholdersDict
            ) if TitleStr else Component.empty()
        SubtitleComp = MiniMessageUtils.processMessage(
            SubtitleStr,PlaceholdersDict
            ) if SubtitleStr else Component.empty()
        
        # 创建Times对象设置淡入、停留和淡出时间
        Times = Title.Times.times(
            Duration.ofMillis(FadeIn * 50),  # ticks转换为毫秒
            Duration.ofMillis(Stay * 50),
            Duration.ofMillis(FadeOut * 50)
        )
        
        # 创建完整的Title对象
        TitleObj = Title.title(TitleComp, SubtitleComp, Times)
        Target.showTitle(TitleObj)

    @staticmethod
    def sendActionBar(Target, MessageObj, PlaceholdersDict=None):
        '''给玩家发送动作栏消息

        参数:
            Target: 目标玩家
            MessageObj: 消息内容
            PlaceholdersDict: 可选的占位符字典
        '''
        if not isinstance(Target, Player) or MessageObj is None:
            return
        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendActionBar(Comp)

    @staticmethod
    def playSound(Target, SoundStr, Volume=1.0, Pitch=1.0):
        '''给玩家播放声音

        参数:
            Target: 目标玩家
            SoundStr: 声音类型 (命名空间键字符串或声音名称)
            Volume: 音量
            Pitch: 音调
        '''
        if not isinstance(Target, Player) or SoundStr is None:
            return
        # 如果已经是Sound枚举实例，直接使用
        if isinstance(SoundStr, Sound):
            Target.playSound(Target.getLocation(), SoundStr, Volume, Pitch)
            return
        # 处理字符串类型的声音
        Namespacedkey = None
        if MiniMessageUtils.isString(SoundStr):
            try:
                if ':' in SoundStr:
                    Namespace, Key = SoundStr.split(':', 1)
                    Namespacedkey = NamespacedKey(Namespace, Key)
                else:
                    # 如果没有指定命名空间，则使用默认命名空间
                    Namespacedkey = NamespacedKey.minecraft(SoundStr.lower())
                registry_sound = Registry.SOUNDS.get(Namespacedkey)
                if registry_sound:
                    Target.playSound(Target.getLocation(), registry_sound, Volume, Pitch)
                    return
            except Exception:
                pass

# 脚本启动检查
if ps.script.isScriptRunning("JiuWu's_Kitchen.py"):
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Load"),{"Version": "v1.1.6", "Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console,
                                 u"{Prefix} <red>Discord: <gray>https://discord.gg/jyhbPUkG",{"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console,u"{Prefix} <red>QQ群: <gray>299852340",{"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console,
        u"{Prefix} <red>Wiki: <gray>https://gitlab.com/jiuwu02/jiuwus_kitchen_wiki/-/wikis/home",{"Prefix": Prefix})
    ServerPluginLoad()
    ReloadPlugin()
