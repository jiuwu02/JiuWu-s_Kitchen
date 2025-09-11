#coding: UTF-8
import math
import random
import json

import pyspigot as ps  # type: ignore

from org.bukkit import Location, Bukkit, Material, Sound  # type: ignore
from org.bukkit.util import Transformation  # type: ignore
from org.bukkit.block import BlockFace  # type: ignore
from org.bukkit.entity import Player, EntityType, ItemDisplay  # type: ignore
from org.bukkit.inventory import EquipmentSlot, ItemStack  # type: ignore
from org.bukkit.event.player import PlayerInteractEvent  # type: ignore
from org.bukkit.event.block import BlockBreakEvent, Action  # type: ignore

from java.lang import System  # type: ignore
from org.joml import Vector3f, Quaternionf  # type: ignore

from net.kyori.adventure.text.minimessage import MiniMessage  # type: ignore
from net.kyori.adventure.title import Title  # type: ignore
from net.kyori.adventure.util import Ticks  # type: ignore
from net.kyori.adventure.text import Component  # type: ignore

CraftEngineAvailable = False
MMOItemsAvailable = False

def ServerPluginLoad():
    """
    在插件加载时检查CraftEngine和MMOItems插件是否可用，并注册相关事件监听器
    """
    global CraftEngineAvailable, MMOItemsAvailable

    # 检查并设置CraftEngine插件的可用性
    CraftEngineAvailable = Bukkit.getPluginManager().isPluginEnabled("CraftEngine")
    if CraftEngineAvailable:
        SendMessage(
            Bukkit.getServer().getConsoleSender(),
            LoadConfig().getString("Messages.PluginLoad.CraftEngine"),
        )
        from net.momirealms.craftengine.bukkit.api.event import (  # type: ignore
            CustomBlockInteractEvent,
            CustomBlockBreakEvent,
        )
        # 注册CraftEngine相关事件监听器
        ps.listener.registerListener(InteractionCraftEngineBlock, CustomBlockInteractEvent)
        ps.listener.registerListener(BreakCraftEngineBlock, CustomBlockBreakEvent)

    # 检查并设置MMOItems插件的可用性
    MMOItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("MMOItems")
    if MMOItemsAvailable:
        SendMessage(
            Bukkit.getServer().getConsoleSender(),
            LoadConfig().getString("Messages.PluginLoad.MMOItems"),
        )

def SetDefaultWithComments(ConfigFile, Path, DefaultValue, Comments = None):
    """为配置项设置默认值和注释

    参数
        ConfigFile: 配置文件对象
        Path: 配置项路径
        DefaultValue: 默认值
        Comments: 注释列表(可选)
    """
    if not ConfigFile.contains(Path):
        ConfigFile.setIfNotExists(Path, DefaultValue)
        if Comments is not None: ConfigFile.setComments(Path, Comments)

def LoadConfig():
    """加载并初始化插件配置文件

    返回
        配置对象
    """
    ConfigPath = "SimpleKitchen/Config.yml"
    ConfigFile = ps.config.loadConfig(ConfigPath)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Drop", True, [u"砧板处理完成后是否掉落成品"])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.StealthInteraction", True, [
        u"是否需要在潜行状态下与砧板交互",
        u"启用时: 玩家必须潜行才能使用砧板功能",
        u"禁用时: 玩家可直接交互无需潜行"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Custom", False, [
        u"是否使用自定义方块作为砧板",
        u"启用时: 使用兼容插件的方块 (例如: CraftEngine)",
        u"禁用时: 使用原版的方块"
        "",
        u"CraftEngine的方块: craftengine <Key>:<ID>"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Material", "OAK_LOG")
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.SpaceRestriction", False, [
        u"砧板上方是否允许存在方块",
        u"启用时: 砧板上方有方块时无法使用",
        u"禁用时: 砧板上方允许存在方块"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.KitchenKnife.Custom", False, [
        u"是否使用自定义刀具",
        u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
        u"禁用时: 使用原版物品"
        "",
        u"CraftEngine物品: craftengine <Key>:<ID>",
        u"MMOItems物品: mmoitems <Type>:<ID>"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Damage.Enable", True, [
        u"是否启用砧板事件",
        u"启用时: 切菜时有概率切伤手指"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Damage.Chance", 10)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.Damage.Value", 2)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.KitchenKnife.Material", "IRON_AXE")
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Offset.X", 0.5)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Offset.Y", 1.0)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Offset.Z", 0.5)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.X", 90.0)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.Y", 0.0)
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Rotation.Z", 0.0, [
        u"允许Z轴旋转角度为小数 (0.0, 360.0)",
        u"也允许为一个范围值随机数 (0.0-360.0)"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.ChoppingBoard.DisplayEntity.Scale", 0.5)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Drop", True, [
        u"炒锅烹饪完成后是否掉落成品"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.StealthInteraction", True, [
        u"控制与炒锅交互是否需要潜行",
        "",
        u"启用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都需要潜行状态",
        u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"不需要\" 潜行状态",
        "",
        u"禁用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都不需要潜行状态",
        u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"需要\" 潜行状态"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Custom", False, [
        u"是否使用自定义炒锅方块",
        u"启用时: 使用兼容插件的方块(例如: CraftEngine)",
        u"禁用时: 使用原版方块"
        "",
        u"CraftEngine的方块: craftengine <Key>:<ID>"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Material", "IRON_BLOCK")
    SetDefaultWithComments(ConfigFile, "Setting.Wok.HeatControl", {
        "CAMPFIRE": 1,
        "MAGMA_BLOCK": 2,
        "LAVA": 3,
    }, [
        u"定义不同热源的烹饪强度",
        u"数值越高代表火候越猛",
        "",
        u"支持 CraftEngine 插件的方块/家具",
        u"CraftEngine的方块: craftengine <Key>:<ID>: <火候大小>"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.NeedBowl", True, [
        u"控制从炒锅盛出成品是否需要碗",
        u"启用时: 必须手持碗才能盛出成品",
        u"禁用时: 空手即可直接盛出成品",
        u"注意: 如果启用则盛出操作是否要求潜行由 Setting.Wok.StealthInteraction 控制"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.InvalidRecipeOutput", "STONE", [
        u"该选项用于当玩家放入不完整或无效的食材组合时",
        u"将成品盛出后会得到这个物品作为失败产物"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Damage.Enable", True, [
        u"是否启用炒锅取出食材烫伤事件",
        u"启用时: 如果锅内存在食材并且已经翻炒过，这时候取出食材将会受到伤害",
        u"禁用时: 从炒锅取出食材时将不会受到任何伤害"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Damage.Value", 2)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Failure.Enable", True, [
        u"是否启用炒锅烹饪失败事件",
        u"启用时: 即使食材和步骤都正确，也有概率烹饪失败",
        u"禁用时: 只要食材和步骤正确，烹饪必定成功"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Failure.Chance", 5)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Failure.Type", "BONE_MEAL", [
        u"炒锅烹饪失败时生成的产物类型"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.TimeOut", 30, [
        u"单次翻炒操作后的最大等待时间 (秒)",
        u"每次翻炒操作后会重置此计时器",
        u"计时结束前未再次翻炒: 锅内食材会烧焦变为失败产物"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Spatula.Custom", False, [
        u"是否使用自定义炒菜铲",
        u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
        u"禁用时: 使用原版物品",
        u"CraftEngine物品: craftengine <Key>:<ID>",
        u"MMOItems物品: mmoitems <Type>:<ID>"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.Spatula.Material", "IRON_SHOVEL")
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Offset.X", 0.5)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Offset.Y", 1.0)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Offset.Z", 0.5)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Rotation.X", 90.0)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Rotation.Y", 0.0)
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Rotation.Z", "0.0-90.0", [
        u"允许Z轴旋转角度为小数 (0.0, 360.0)",
        u"也允许为一个范围值随机数 (0.0-360.0)"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Wok.DisplayEntity.Scale", 0.5)
    SetDefaultWithComments(ConfigFile, "Messages.Prefix", u"<gray>[ <dark_gray>JiuWu\'s Kitchen <gray>]")
    SetDefaultWithComments(ConfigFile, "Messages.Load", u"{Prefix} <green>欢迎使用 JiuWu\'s Kitchen {Version} 插件!厨房已就绪! 料理正等待着你的创造!")
    SetDefaultWithComments(ConfigFile, "Messages.Reload.LoadPlugin", u"{Prefix} <green>成功重载 JiuWu\'s Kitchen 插件!")
    SetDefaultWithComments(ConfigFile, "Messages.Reload.LoadChoppingBoardRecipe",u"{Prefix} <green>成功加载 {Amount} 个砧板配方")
    SetDefaultWithComments(ConfigFile, "Messages.Reload.LoadWokRecipe",u"{Prefix} <green>成功加载 {Amount} 个炒锅配方")
    SetDefaultWithComments(ConfigFile, "Messages.InvalidMaterial", u"{Prefix} <red>无效的 {Material} 物品材料")
    SetDefaultWithComments(ConfigFile, "Messages.WokTop", u"<aqua>炒锅中的食材:")
    SetDefaultWithComments(ConfigFile,"Messages.WokContent",u" <gray>{ItemName} <dark_gray>× <yellow>{ItemAmount} <gray>已翻炒: <yellow>{Count}")
    SetDefaultWithComments(ConfigFile, "Messages.WokDown", u"<aqua>总计翻炒次数: <yellow>{Count}")
    SetDefaultWithComments(ConfigFile, "Messages.WokHeatControl", u"<aqua>热源等级: <yellow>{Heat}")
    SetDefaultWithComments(ConfigFile, "Messages.Title.CutHand.MainTitle",u"<red>✄ 哎呀! 切到手了!")
    SetDefaultWithComments(ConfigFile, "Messages.Title.CutHand.SubTitle",u"<gray>你受到了 <red>{Damage} <gray>点伤害! 小心点呀大厨!")
    SetDefaultWithComments(ConfigFile, "Messages.Title.Scald.MainTitle", u"<red>🔥 沸沸沸! 烫烫烫!")
    SetDefaultWithComments(ConfigFile, "Messages.Title.Scald.SubTitle", u"<gray>你受到了 <red>{Damage} <gray>点伤害! 小心点呀大厨!")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.TakeOffItem", u"<gray>提示: 空手右键点击砧板可取下食材")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.WokNoItem", u"<red>炒锅中没有任何食材!")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.AddWokItem", u"<green>向炒锅添加了 {Material} 食材")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.CutAmount", u"<gray>切割进度: <green>{CurrentCount} <dark_gray>/ <green>{NeedCount}")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.StirCount", u"<gray>翻炒次数: <green>{Count}")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.ErrorRecipe", u"<red>✗ 配方错误! 你可真失败!")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.FailureRecipe",u"<red>✗ 失败的配方! 真是浪费这么好的食材了!")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.SuccessRecipe",u"<green>✓ 成功的配方! 不愧是大厨!")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.CannotCut",u"<red>✗ 这个食材无法处理")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.WokAddItem",u"<green>向炒锅添加了 <gray>{Material} <green>食材")
    SetDefaultWithComments(ConfigFile, "Messages.ActionBar.BurntFood",u"<red>✗ 糟糕透了! 食材全糊了!")
    SetDefaultWithComments(ConfigFile, "Messages.PluginLoad.CraftEngine", u"{Prefix} <green>检测到 CraftEngine 插件")
    SetDefaultWithComments(ConfigFile, "Messages.PluginLoad.MMOItems", u"{Prefix} <green>检测到 MMOItems 插件")
    SetDefaultWithComments(ConfigFile, "Setting.Sound.ChoppingBoardAddItem", u"entity.item_frame.add_item", [
        u"砧板添加食材的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.ChoppingBoardCutItem", u"item.axe.strip", [
        u"砧板切割食材的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.ChoppingBoardCutHand", u"entity.player.hurt", [
        u"砧板切割时手被切伤的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.WokAddItem", u"block.anvil.hit", [
        u"炒锅添加食材的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.WokStirItem", u"block.lava.extinguish", [
        u"炒锅翻炒食材的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.WokScald", u"entity.player.hurt_on_fire", [
        u"炒锅翻炒时手被烫伤的音效"
    ])
    SetDefaultWithComments(ConfigFile, "Setting.Sound.WokTakeOffItem", u"entity.item.pickup", [
        u"炒锅取出食材的音效"
    ])
    ConfigFile.save()
    return ps.config.loadConfig(ConfigPath)

def LoadChoppingBoardRecipe():
    """加载砧板配方配置文件

    返回: 
        对象: 砧板配方文件
    """
    ChoppingBoardRecipePath = "SimpleKitchen/Recipe/ChoppingBoard.yml"
    return ps.config.loadConfig(ChoppingBoardRecipePath)

def LoadWokRecipe():
    """加载炒锅配方配置文件

    返回: 
        对象: 砧板配方文件
    """
    WokRecipePath = "SimpleKitchen/Recipe/Wok.yml"
    return ps.config.loadConfig(WokRecipePath)

def LoadData():
    """加载数据文件

    返回:
        对象: 数据文件
    """
    DataPath = "SimpleKitchen/Data.yml"
    return ps.config.loadConfig(DataPath)

def InteractionCraftEngineBlock(E):
    """处理CraftEngine方块的交互事件

    参数
        E: BlockInteractEvent事件对象
    """
    from net.momirealms.craftengine.core.entity.player import InteractionHand  # type: ignore
    from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
    Config = LoadConfig()
    # 判断是否为主手
    if E.hand() != InteractionHand.MAIN_HAND:
        return
    ClickPlayer = E.player()
    ClickBlock = E.bukkitBlock()
    # 判断是否为空方块
    if ClickBlock is None:
        return
    FileKey = GetFileKey(ClickBlock)
    DataFile = LoadData()
    # 判断CraftEngine方块是否为砧板
    if Config.getBoolean("Setting.ChoppingBoard.Custom"):
        Identifier, ID = Config.getString("Setting.ChoppingBoard.Material").split(" ", 1)
        if Identifier != "craftengine":
            return
        ClickBlockState = CraftEngineBlocks.getCustomBlockState(ClickBlock)
        if str(ClickBlockState) == ID:
            if not Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
                if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR: return
            if E.action() != E.Action.RIGHT_CLICK: return
            StealthSetting = Config.getBoolean("Setting.ChoppingBoard.StealthInteraction")
            if StealthSetting:
                if not ClickPlayer.isSneaking(): return
            else:
                if ClickPlayer.isSneaking(): return
            E.setCancelled(True)
            HasExistingDisplay = DataFile.contains("ChoppingBoard." + FileKey)
            InteractionChoppingBoard(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return
    # 判断CraftEngine方块是否为炒锅
    elif Config.getBoolean("Setting.Wok.Custom"):
        Identifier, ID = Config.getString("Setting.Wok.Material").split(" ", 1)
        if Identifier != "craftengine":
            return
        ClickBlockState = CraftEngineBlocks.getCustomBlockState(ClickBlock)
        if str(ClickBlockState) == ID:
            HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
            BottomBlock = ClickBlock.getRelative(BlockFace.DOWN).getType().name()
            HeatLevel = Config.getString("Setting.Wok.HeatControl." + BottomBlock)
            if BottomBlock not in HeatControl: return
            if E.action() == E.Action.LEFT_CLICK:
                if Config.getBoolean("Setting.Wok.StealthInteraction"):
                    if not ClickPlayer.isSneaking(): return
                else:
                    if ClickPlayer.isSneaking(): return
                MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
                if not IsToolItem(MainHandItem, Config, "Wok"): return
                FileKey = GetFileKey(ClickBlock)
                HasExistingDisplay = DataFile.get("Wok")
                if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
                else: HasExistingDisplay = False
                if HasExistingDisplay:
                    E.setCancelled(True)
                    OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel)
                else:
                    E.setCancelled(True)
                    SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                return
            if E.action() != E.Action.RIGHT_CLICK: return
            E.setCancelled(True)
            FileKey = GetFileKey(ClickBlock)
            HasExistingDisplay = DataFile.get("Wok")
            if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
            else: HasExistingDisplay = False
            if Config.getBoolean("Setting.Wok.StealthInteraction"):
                if not ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock)
                        return
                    return
            else:
                if ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock)
                        return
                    return
            InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return

def InteractionVanillaBlock(E):
    """处理玩家与原版方块的交互事件

    参数
        E: PlayerInteractEvent事件对象
    """
    ClickBlock = E.getClickedBlock()
    if ClickBlock is None: return
    if E.getHand() != EquipmentSlot.HAND: return
    ClickPlayer = E.getPlayer()
    Config = LoadConfig()
    ClickBlockType = ClickBlock.getType().name()
    DataFile = LoadData()
    FileKey = GetFileKey(ClickBlock)
    # 判断点击的方块是否为砧板
    if not Config.getBoolean("Setting.ChoppingBoard.Custom"):
        if ClickBlockType == Config.getString("Setting.ChoppingBoard.Material"):
            if E.getAction() != Action.RIGHT_CLICK_BLOCK: return
            if Config.getBoolean("Setting.ChoppingBoard.StealthInteraction"):
                if not ClickPlayer.isSneaking(): return
            else:
                if ClickPlayer.isSneaking(): return
            if not Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
                if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR: return
            E.setCancelled(True)
            
            HasExistingDisplay = DataFile.contains("ChoppingBoard." + FileKey)
            InteractionChoppingBoard(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return
    # 判断点击的方块是否为炒锅
    if not Config.getBoolean("Setting.Wok.Custom"):
        if ClickBlockType == Config.getString("Setting.Wok.Material"):
            HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
            BottomBlock = ClickBlock.getRelative(BlockFace.DOWN).getType().name()
            HeatLevel = Config.getString("Setting.Wok.HeatControl." + BottomBlock)
            if BottomBlock not in HeatControl: return
            if E.getAction() == Action.LEFT_CLICK_BLOCK:
                if Config.getBoolean("Setting.Wok.StealthInteraction"):
                    if not ClickPlayer.isSneaking(): return
                else:
                    if ClickPlayer.isSneaking(): return
                MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
                if not IsToolItem(MainHandItem, Config, "Wok"): return
                FileKey = GetFileKey(ClickBlock)
                HasExistingDisplay = DataFile.get("Wok")
                if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
                else: HasExistingDisplay = False
                if HasExistingDisplay:
                    E.setCancelled(True)
                    OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel)
                else:
                    E.setCancelled(True)
                    SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                return
            if E.getAction() != Action.RIGHT_CLICK_BLOCK: return
            E.setCancelled(True)
            FileKey = GetFileKey(ClickBlock)
            HasExistingDisplay = DataFile.get("Wok")
            if HasExistingDisplay: HasExistingDisplay = HasExistingDisplay.contains(FileKey)
            else: HasExistingDisplay = False
            if Config.getBoolean("Setting.Wok.StealthInteraction"):
                if not ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock)
                        return
                    return
            else:
                if ClickPlayer.isSneaking():
                    if not Config.getBoolean("Setting.Wok.NeedBowl"):
                        GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock)
                        return
                    return
            InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay)
            return

def BreakVanillaBlock(E):
    """处理砧板方块被破坏的事件

    参数
        E: BlockBreakEvent事件对象
    """
    Block = E.getBlock()
    Config = LoadConfig()
    DataFile = LoadData()
    FileKey = GetFileKey(Block)
    
    # 处理砧板方块
    ChoppingBoard = Config.getBoolean("Setting.ChoppingBoard.Custom")
    if not ChoppingBoard:
        try:
            MaterialSetting = Config.getString("Setting.ChoppingBoard.Material")
            if Block.getType() == Material.valueOf(MaterialSetting):
                HasExistingDisplay = DataFile.contains("ChoppingBoard." + FileKey)
                if HasExistingDisplay:
                    DisplayLocation = CalculateDisplayLocation(Block, Config)
                    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
                    if ItemDisplayEntity:
                        DisplayItem = ItemDisplayEntity.getItemStack()
                        if DisplayItem:
                            ItemEntity = Block.getWorld().dropItem(ItemDisplayEntity.getLocation(), DisplayItem)
                            ItemEntity.setPickupDelay(0)
                        ItemDisplayEntity.remove()
                    DataFile.set("ChoppingBoard." + FileKey, None)
                    DataFile.save()
                return
        except: 
            pass
    # 处理炒锅方块
    Wok = Config.getBoolean("Setting.Wok.Custom")
    if not Wok:
        try:
            MaterialSetting = Config.getString("Setting.Wok.Material")
            if Block.getType() == Material.valueOf(MaterialSetting):
                HasExistingDisplay = DataFile.contains("Wok." + FileKey)
                if HasExistingDisplay:
                    # 获取炒锅上方的所有展示实体并掉落他
                    DisplayLocation = CalculateWokDisplayLocation(Block, Config)
                    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                    if NearbyDisplays:
                        for Display in NearbyDisplays:
                            if Display and not Display.isDead():
                                DisplayItem = Display.getItemStack()
                                if DisplayItem:
                                    # 直接使用展示实体的ItemStack掉落物品
                                    ItemEntity = Block.getWorld().dropItem(Display.getLocation(), DisplayItem)
                                    ItemEntity.setPickupDelay(0)
                                Display.remove()
                    # 清除数据文件中的炒锅数据
                    DataFile.set("Wok." + FileKey, None)
                    DataFile.save()
                return
        except:
            pass

def BreakCraftEngineBlock(E):
    """处理CraftEngine方块被破坏的事件

    参数
        E: CustomBlockBreakEvent事件对象
    """
    BreakBlock = E.bukkitBlock()
    if BreakBlock is None: 
        return
    
    Config = LoadConfig()
    DataFile = LoadData()
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
                        HasExistingDisplay = DataFile.contains("ChoppingBoard." + FileKey)
                        if HasExistingDisplay:
                            DisplayLocation = CalculateDisplayLocation(BreakBlock, Config)
                            ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
                            if ItemDisplayEntity:
                                DisplayItem = ItemDisplayEntity.getItemStack()
                                if DisplayItem:
                                    ItemEntity = BreakBlock.getWorld().dropItem(
                                        ItemDisplayEntity.getLocation(), 
                                        DisplayItem
                                    )
                                    ItemEntity.setPickupDelay(0)
                                ItemDisplayEntity.remove()
                            DataFile.set("ChoppingBoard." + FileKey, None)
                            DataFile.save()
                        return
                except: 
                    pass
    
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
                        HasExistingDisplay = DataFile.contains("Wok." + FileKey)
                        if HasExistingDisplay:
                            # 获取炒锅上方的所有展示实体并掉落它们
                            DisplayLocation = CalculateWokDisplayLocation(BreakBlock, Config)
                            NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                            if NearbyDisplays:
                                for Display in NearbyDisplays:
                                    if Display and not Display.isDead():
                                        DisplayItem = Display.getItemStack()
                                        if DisplayItem:
                                            # 直接使用展示实体的ItemStack掉落物品
                                            ItemEntity = BreakBlock.getWorld().dropItem(Display.getLocation(), DisplayItem)
                                            ItemEntity.setPickupDelay(0)
                                        Display.remove()
                            # 清除数据文件中的炒锅数据
                            DataFile.set("Wok." + FileKey, None)
                            DataFile.save()
                        return
                except:
                    pass

def CreateItemDisplay(Location, Item, Config, Target):
    """创建物品展示实体并设置属性

    参数
        Location: 生成位置
        Item: 展示的物品
        Config: 配置对象
        Target: 配方目标
    返回
        创建的展示实体
    """
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
            except ValueError:
                RotZ = 0.0
        else:
            try:
                RotZ = float(RotZConfig)
            except ValueError:
                RotZ = 0.0
    else:
        try:
            RotZ = float(RotZConfig)
        except ValueError:
            RotZ = 0.0
            
    RadX = math.radians(RotX)
    RadY = math.radians(RotY)
    RadZ = math.radians(RotZ)
    Rotation = Quaternionf().rotationXYZ(RadX, RadY, RadZ)
    New_Transform = Transformation(
        Vector3f(),
        Rotation,
        ScaleVector,
        Quaternionf()
    )
    ItemDisplayEntity.setTransformation(New_Transform)
    ItemDisplayEntity.setInvulnerable(True)
    ItemDisplayEntity.setSilent(True)
    ItemDisplayEntity.setPersistent(True)
    ItemDisplayEntity.setGravity(False)
    ItemDisplayEntity.setCustomNameVisible(False)
    return ItemDisplayEntity

def FindNearbyDisplay(Location):
    """在指定位置附近查找物品展示实体

    参数
        Location: 查找位置
    返回
        找到的物品展示实体或None
    """
    FoundEntities = []
    for entity in Location.getWorld().getNearbyEntities(Location, 0.1, 0.1, 0.1):
        if entity.getType() == EntityType.ITEM_DISPLAY:
            FoundEntities.append(entity)
    return FoundEntities if FoundEntities else None

def GetFileKey(Block):
    """获取砧板的数据文件键

    参数
        Block: 砧板方块
    返回
        数据文件键
    """
    GetCoordKey = "{},{},{},{}".format(
        int(Block.getX()),
        int(Block.getY()),
        int(Block.getZ()),
        Block.getWorld().getName()
    )
    return "{}".format(GetCoordKey)

def CalculateDisplayLocation(BaseLocation, Config):
    """计算物品展示实体的位置

    参数
        BaseLocation: 基础位置
        Config: 配置对象
    返回
        展示实体的位置
    """
    Offset_X = Config.getDouble("Setting.ChoppingBoard.DisplayEntity.Offset.X", 0.0)
    Offset_Y = Config.getDouble("Setting.ChoppingBoard.DisplayEntity.Offset.Y", 0.0)
    Offset_Z = Config.getDouble("Setting.ChoppingBoard.DisplayEntity.Offset.Z", 0.0)
    return Location(
        BaseLocation.getWorld(),
        BaseLocation.getX() + Offset_X,
        BaseLocation.getY() + Offset_Y,
        BaseLocation.getZ() + Offset_Z
    )

def GiveItemToPlayer(Player, Item):
    """给予玩家物品，处理背包空间不足的情况

    参数
        Player: 目标玩家
        Item: 要给予的物品
    """
    if Player.getInventory().firstEmpty() != -1:
        Player.getInventory().addItem(Item)
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

def HandleCutting(Player, World, X, Y, Z, Config):
    """处理砧板上的切割操作

    参数
        Player: 执行切割的玩家
        World: 砧板所在的世界
        X: 砧板的X坐标
        Y: 砧板的Y坐标
        Z: 砧板的Z坐标
        Config: 配置对象
    """
    BaseLocation = Location(World, X, Y, Z)
    DisplayLocation = CalculateDisplayLocation(BaseLocation, Config)
    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)[0]
    if not ItemDisplayEntity: return
    DisplayItem = ItemDisplayEntity.getItemStack()
    if not DisplayItem: return
    RecipeConfig = LoadChoppingBoardRecipe()
    ItemMaterial = GetItemIdentifier(DisplayItem)
    RequiredCuts = RecipeConfig.getInt(ItemMaterial + ".Count")
    ResultMaterial = RecipeConfig.getString(ItemMaterial + ".Output")
    if not RequiredCuts: return
    CoordKey = "{},{},{},{}".format(int(X), int(Y), int(Z), World.getName())
    FileKey = "ChoppingBoard.{}".format(CoordKey)
    DataFile = LoadData()
    CurrentCuts = DataFile.getInt(FileKey, 0)
    CurrentCuts += 1
    DataFile.set(FileKey, CurrentCuts)
    DataFile.save()
    if (Config.getBoolean("Setting.ChoppingBoard.Damage.Enable") and 
        random.randint(1, 100) <= Config.getInt("Setting.ChoppingBoard.Damage.Chance")):
        DamageValue = Config.getInt("Setting.ChoppingBoard.Damage.Value")
        Player.damage(DamageValue)
        SendSound(Player, Config.get("Setting.Sound.ChoppingBoardCutHand"))
        
        MainTitle = Config.getString("Messages.Title.CutHand.MainTitle")
        SubTitle = Config.getString("Messages.Title.CutHand.SubTitle")
        SubTitle = SubTitle.format(Damage = str(DamageValue))
        MainTitleComponent = MiniMessage.miniMessage().deserialize(MainTitle)
        SubTitleComponent = MiniMessage.miniMessage().deserialize(SubTitle)
        fadeInDuration = Ticks.duration(10)
        stayDuration = Ticks.duration(20)
        fadeOutDuration = Ticks.duration(10)
        TitleObj = Title.title(
            MainTitleComponent,
            SubTitleComponent,
            Title.Times.of(fadeInDuration, stayDuration, fadeOutDuration)
        )
        Player.showTitle(TitleObj)
        
    ActionBarMessage = Config.getString("Messages.ActionBar.CutAmount")
    ActionBarMessage = ActionBarMessage.format(CurrentCount = str(CurrentCuts), NeedCount = str(RequiredCuts))
    SendActionBar(Player, ActionBarMessage)
    SendSound(Player, Config.get("Setting.Sound.ChoppingBoardCutItem"))
    if CurrentCuts >= RequiredCuts:
        if " " in ResultMaterial:
            GiveItem = ResultMaterial
        else:
            GiveItem = RequiredCuts
        ResultItemStack = CreateItemStack(GiveItem)
        if not ResultItemStack:
            SendMessage(Bukkit.getServer().getConsoleSender(),
                        Config.getString("Messages.InvalidMaterial")
                       .replace("{Material}", ResultMaterial))
            return
        if ResultItemStack is not None:
            ItemDisplayEntity.remove()
            DropLocation = Location(World, X + 0.5, Y + 1.0, Z + 0.5)
            if Config.getBoolean("Setting.ChoppingBoard.Drop"):
                ItemEntity = World.dropItem(DropLocation, ResultItemStack)
                ItemEntity.setPickupDelay(20)
            else:
                GiveItemToPlayer(Player, ResultItemStack)
            DataFile.set(FileKey, None)
            DataFile.save()
        else:
            SendMessage(Bukkit.getServer().getConsoleSender(), Config.getString("Messages.InvalidMaterial")
                       .replace("{Material}", ResultMaterial))
            return

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
    DataFile = LoadData()
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if HasExistingDisplay:
            if IsToolItem(MainHandItem, Config, "ChoppingBoard"):
                BlockLoc = Block.getLocation()
                HandleCutting(
                    ClickPlayer,
                    BlockLoc.getWorld(),
                    BlockLoc.getX(),
                    BlockLoc.getY(),
                    BlockLoc.getZ(),
                    Config
                )
                return
            else:
                SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.TakeOffItem"))
                return
        else:
            DisplayItem = MainHandItem.clone()
            DisplayItem.setAmount(1)
            MainHandItem.setAmount(MainHandItem.getAmount() - 1)
            DisplayLocation = CalculateDisplayLocation(Block, Config)
            ItemDisplayEntity = CreateItemDisplay(DisplayLocation, DisplayItem, Config, "ChoppingBoard")
            SendSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardAddItem"))
            if not DataFile.contains("ChoppingBoard." + FileKey):
                DataFile.set(FileKey, 0)
                DataFile.save()
                return
    elif not MainHandItem or MainHandItem.getType() == Material.AIR:
        if HasExistingDisplay:
            DisplayLocation = CalculateDisplayLocation(Block, Config)
            ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)[0]
            if ItemDisplayEntity:
                DisplayItem = ItemDisplayEntity.getItemStack()
                if DisplayItem: ClickPlayer.getInventory().setItemInMainHand(DisplayItem.clone())
                ItemDisplayEntity.remove()
                DataFile.set(FileKey, None)
                DataFile.save()
                return

def CalculateWokDisplayLocation(BaseBlock, Config, ExtraOffset=0):
    """计算炒锅上展示实体的位置
    
    参数
        BaseBlock: 炒锅方块
        Config: 配置对象
        ExtraOffset: 额外偏移量
    """
    Offset_X = Config.getDouble("Setting.Wok.DisplayEntity.Offset.X")
    Offset_Y = Config.getDouble("Setting.Wok.DisplayEntity.Offset.Y")
    Offset_Z = Config.getDouble("Setting.Wok.DisplayEntity.Offset.Z")
    BaseLocation = BaseBlock.getLocation()
    return Location(
        BaseLocation.getWorld(),
        BaseLocation.getX() + Offset_X,
        BaseLocation.getY() + Offset_Y + ExtraOffset,
        BaseLocation.getZ() + Offset_Z
    )

def OutputWokInfo(ClickPlayer, Config, FileKey, HeatLevel):
    '''输出炒锅信息
    
    参数
        ClickPlayer: 玩家对象
        Config: 配置文件对象
        FileKey: 炒锅的坐标和世界名
        HeatLevel: 炒锅的温度等级
    '''
    WokTopMessage = Config.getString("Messages.WokTop")
    WokContent = Config.getString("Messages.WokContent")
    DataFile = LoadData()
    ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
    TotalCount = DataFile.getString("Wok." + FileKey + ".Count")
    SendMessage(ClickPlayer, WokTopMessage)
    for Item in ItemList:
        Parts = Item.split(" ", 3)
        PluginName, ItemName, Amount, Count = Parts
        ItemStack = CreateItemStack(Item)
        MaterialComponent = OutputItemDisplayName(ItemStack)
        ContentParts = WokContent.split("{ItemName}")
        Prefix = ContentParts[0]
        Suffix = ContentParts[1] if len(ContentParts) > 1 else ""
        Suffix = Suffix.replace("{ItemAmount}", Amount).replace("{Count}", Count)
        Builder = Component.text()
        if Prefix:
            Builder.append(MiniMessage.miniMessage().deserialize(ConvertLegacyColors(Prefix)))
        Builder.append(MaterialComponent)
        if Suffix:
            Builder.append(MiniMessage.miniMessage().deserialize(ConvertLegacyColors(Suffix)))
        ClickPlayer.sendMessage(Builder.build())
    WokDown = Config.getString("Messages.WokDown").replace("{Count}", TotalCount)
    SendMessage(ClickPlayer, WokDown)
    HeatControl = Config.getString("Messages.WokHeatControl").replace("{Heat}", HeatLevel)
    SendMessage(ClickPlayer, HeatControl)

def InteractionWok(ClickPlayer, ClickBlock, Config, FileKey, HasExistingDisplay):
    '''处理炒锅的交互事件
    
    参数
        ClickPlayer: 玩家对象
        ClickBlock: 点击的方块对象
        Config: 配置文件对象
        FileKey: 炒锅的坐标和世界名
        HasExistingDisplay: 炒锅是否已经有显示物
    '''
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    DataFile = LoadData()
    # 判断主手物品是否为工具
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if IsToolItem(MainHandItem, Config, "Wok"):
            # 执行翻炒动作
            ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
            if not ItemList:
                SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                return
            # 检查时间戳
            LastStirTime = DataFile.getLong("Wok." + FileKey + ".LastStirTime", 0)
            # 更新翻炒次数
            StirCount = DataFile.getInt("Wok." + FileKey + ".Count", 0)
            if StirCount != 0:
                CurrentTime = System.currentTimeMillis()
                if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                    SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                    return
            # 更新时间戳
            DataFile.set("Wok." + FileKey + ".LastStirTime", System.currentTimeMillis())
            StirCount += 1
            DataFile.set("Wok." + FileKey + ".Count", StirCount)
            # 更新炒锅内物品的翻炒次数
            UpdatedItemList = []
            for ItemEntry in ItemList:
                Parts = ItemEntry.split(" ")
                ItemType = Parts[0]
                ItemID = Parts[1]
                Quantity = int(Parts[2])
                StirTimes = int(Parts[3]) + 1
                UpdatedEntry = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                UpdatedItemList.append(UpdatedEntry)
            DataFile.set("Wok." + FileKey + ".Items", UpdatedItemList)
            DataFile.save()
            SendActionBar(ClickPlayer,
                          Config.getString("Messages.ActionBar.StirCount").replace("{Count}", str(StirCount)))
            SendSound(ClickPlayer, Config.get("Setting.Sound.WokStirItem"))
            return
        # 检查是否需要碗
        BowlCustom = Config.getBoolean("Setting.Wok.NeedBowl")
        if BowlCustom and MainHandItem.getType() == Material.BOWL:
            # 执行使用碗将成品盛出炒锅
            GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock)
            return
        # 判断是否已经创建了这个炒锅
        if HasExistingDisplay:
            CurrentItemIdentifier = GetItemIdentifier(MainHandItem)
            ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
            NeedAddItem = False
            DisplayLocation = CalculateWokDisplayLocation(ClickBlock, Config)
            NearbyDisplays = FindNearbyDisplay(DisplayLocation)
            
            for Index, ItemEntry in enumerate(ItemList):
                Parts = ItemEntry.split(" ")
                ItemTypeID = Parts[0] + " " + Parts[1]
                # 判断是否已经添加过这个食材
                if ItemTypeID == CurrentItemIdentifier:
                    CurrentAmount = int(Parts[2]) + 1
                    StirCount = int(Parts[3])
                    ItemList[Index] = ItemTypeID + " " + str(CurrentAmount) + " " + str(StirCount)
                    NeedAddItem = True
                    
                    for Display in NearbyDisplays:
                        if Display and not Display.isDead():
                            DisplayItem = Display.getItemStack()
                            if DisplayItem and GetItemIdentifier(DisplayItem) == CurrentItemIdentifier:
                                DisplayItem.setAmount(CurrentAmount)
                                Display.setItemStack(DisplayItem)
                                break
                    break
            # 判断是否需要添加新的食材
            if not NeedAddItem:
                ItemListLength = len(ItemList)
                ExtraOffset = 0.0001 * ItemListLength
                ItemList.append(CurrentItemIdentifier + " 1 0")
                DisplayItem = MainHandItem.clone()
                DisplayLocation = CalculateWokDisplayLocation(ClickBlock, Config, ExtraOffset)
                CreateItemDisplay(DisplayLocation, DisplayItem, Config, "Wok")
            DataFile.set("Wok." + FileKey + ".Items", list(ItemList))
            DataFile.save()
            MessageTemplate = Config.getString("Messages.ActionBar.WokAddItem")
            MaterialComponent = OutputItemDisplayName(MainHandItem)
            SendActionBarWithMaterial(ClickPlayer, MessageTemplate, MaterialComponent)
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            SendSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            return
        # 没添加这个炒锅，直接在数据文件中创建一个炒锅数据
        else:
            SaveValue = GetItemIdentifier(MainHandItem) + " 1 0"
            DataFile.set("Wok." + FileKey + ".Items", [SaveValue])
            DataFile.set("Wok." + FileKey + ".Count", 0)
            DataFile.save()
            DisplayItem = MainHandItem.clone()
            DisplayLocation = CalculateWokDisplayLocation(ClickBlock, Config)
            CreateItemDisplay(DisplayLocation, DisplayItem, Config, "Wok")
            MessageTemplate = Config.getString("Messages.ActionBar.WokAddItem")
            MaterialComponent = OutputItemDisplayName(MainHandItem)
            SendActionBarWithMaterial(ClickPlayer, MessageTemplate, MaterialComponent)
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            SendSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            return
    else:
        # 判断是否翻炒过
        if DataFile.getInt("Wok." + FileKey + ".Count") > 0:
            # 获取配置文件中是否启用伤害模块
            if Config.getBoolean("Setting.Wok.Damage.Enable"):
                DamageValue = Config.getInt("Setting.Wok.Damage.Value")
                ClickPlayer.damage(DamageValue)
                SendSound(ClickPlayer, Config.get("Setting.Sound.WokScald"))
                MainTitle = Config.getString("Messages.Title.Scald.MainTitle")
                SubTitle = Config.getString("Messages.Title.Scald.SubTitle")
                SubTitle = SubTitle.format(Damage = str(DamageValue))
                MainTitleComponent = MiniMessage.miniMessage().deserialize(MainTitle)
                SubTitleComponent = MiniMessage.miniMessage().deserialize(SubTitle)
                fadeInDuration = Ticks.duration(10)
                stayDuration = Ticks.duration(20)
                fadeOutDuration = Ticks.duration(10)
                TitleObj = Title.title(
                    MainTitleComponent,
                    SubTitleComponent,
                    Title.Times.of(fadeInDuration, stayDuration, fadeOutDuration)
                )
                ClickPlayer.showTitle(TitleObj)
        # 执行按顺序取出食材
        ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
        if not ItemList:
            SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
            return
        LastItemEntry = ItemList[-1]
        Parts = LastItemEntry.split(" ")
        ItemType = Parts[0]
        ItemID = Parts[1]
        Quantity = int(Parts[2])
        StirTimes = int(Parts[3])
        Quantity -= 1
        ItemToGive = CreateItemStack(LastItemEntry)
        if ItemToGive:
            GiveItemToPlayer(ClickPlayer, ItemToGive)
        if Quantity <= 0:
            ItemList.pop()
            if not ItemList:
                DataFile.set("Wok." + FileKey, None)
            else:
                DataFile.set("Wok." + FileKey + ".Items", ItemList)
            DisplayLocation = CalculateWokDisplayLocation(ClickBlock, Config)
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
            DataFile.set("Wok." + FileKey + ".Items", ItemList)
        DataFile.save()

def GetWokOutput(DataFile, Config, FileKey, ClickPlayer, ClickBlock):
    '''获取炒锅的输出
    
    参数：
        DataFile - 数据文件
        Config - 配置文件
        FileKey -  cooking_wok_data 文件的键值
        ClickPlayer - 点击的玩家
        ClickBlock - 点击的方块
    '''
    DataStirFryAmount = DataFile.getInt("Wok." + FileKey + ".Count")
    if DataStirFryAmount == 0: return
    ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
    if not ItemList:
        SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
        return
    HeatControl = Config.getConfigurationSection("Setting.Wok.HeatControl")
    HeatControlLevel = 0
    if HeatControl: HeatControlLevel = HeatControl.getInt(ClickBlock.getRelative(BlockFace.DOWN).getType().name(), 0)
    RecipeConfig = LoadWokRecipe()
    RecipeKeys = RecipeConfig.getKeys(False)
    # 遍历所有配方
    for RecipeKey in RecipeKeys:
        RecipeHeat = RecipeConfig.getInt(RecipeKey + ".HeatControl", 0)
        if RecipeHeat != HeatControlLevel or HeatControlLevel == 0: continue
        RecipeItemList = RecipeConfig.getStringList(RecipeKey + ".Item")
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
            Tolerance = RecipeConfig.getInt(RecipeKey + ".FaultTolerance")
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
        # 匹配配方被找到
        if Match:
            StirFryAmount = RecipeConfig.get(RecipeKey + ".Count")
            SendSound(ClickPlayer, Config.get("Setting.Sound.WokTakeOffItem"))
            if "-" in StirFryAmount:
                MaxValue, MinValue = StirFryAmount.split("-")
                RandRange = range(int(MaxValue), int(MinValue))
                MaxValue = max(RandRange)
                MinValue = min(RandRange)
            else:
                MaxValue = RecipeConfig.getInt(RecipeKey + ".Count")
                MinValue = RecipeConfig.getInt(RecipeKey + ".Count")
            LastStirTime = DataFile.getLong("Wok." + FileKey + ".LastStirTime", 0)
            CurrentTime = System.currentTimeMillis()
            if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                RawItem = RecipeConfig.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            if DataStirFryAmount > MaxValue:
                BurntItem = RecipeConfig.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, BurntItem, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            elif DataStirFryAmount < MinValue:
                RawItem = RecipeConfig.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            if Config.getBoolean("Setting.Wok.Failure.Enable"):
                Chance = Config.getInt("Setting.Wok.Failure.Chance")
                if random.randint(1, 100) < Chance:
                    ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
                    OutputWokItem(RecipeKey, ErrorRecipe, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                    SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.FailureRecipe"))
                    return
            if Amount <= Tolerance:
                OutputWokItem(RecipeKey, RecipeKey, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.SuccessRecipe"))
                return
            elif GreaterThan > LessThan:
                BurntItem = RecipeConfig.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
            elif LessThan > GreaterThan:
                RawItem = RecipeConfig.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, RawItem, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
                return
        # 没找到配方
        else: continue
    # 没有任何可以匹配的配方，直接输出错误配方
    if Config.getBoolean("Setting.Wok.Failure.Enable"):
        ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
        OutputWokItem(RecipeKey, ErrorRecipe, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock, Config)
        SendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ErrorRecipe"))

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
        ITEM = CreateItemStack(Item)
        ITEM.setAmount(GiveAmount)
    else:
        try:
            Parts = Item.split(" ", 2)
            ITEM = CreateItemStack(Item)
            ITEM.setAmount(int(Parts[2]))
        except: return
    GiveItemToPlayer(ClickPlayer, ITEM)
    DataFile.set("Wok." + FileKey, None)
    DataFile.save()
    DisplayLocation = CalculateWokDisplayLocation(ClickBlock, Config)
    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
    if NearbyDisplays:
        for display in NearbyDisplays: display.remove()

def CreateItemStack(ItemKey, Amount = 1):
    '''创建物品栈

    参数
        ItemKey: 物品键
        Amount: 数量
    
    返回
        ItemStack: 物品栈
    '''
    if not ItemKey: return
    Parts = ItemKey.split(" ")
    if len(Parts) < 1: return None
    ItemType = Parts[0]
    if Amount != 1:
        try:
            Amount = int(Parts[2])
        except:
            pass
    
    if ItemType == "minecraft":
        try:
            Item = Material.valueOf(Parts[1])
            return ItemStack(Item, Amount)
        except: return None
    elif ItemType == "craftengine" and CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            from net.momirealms.craftengine.core.util import Key  # type: ignore
            KeyParts = Parts[1].split(":")
            CraftEngineItem = CraftEngineItems.byId(Key(KeyParts[0], KeyParts[1])).buildItemStack()
            CraftEngineItem.setAmount(Amount)
            return CraftEngineItem
        except: return None
    elif ItemType == "mmoitems" and MMOItemsAvailable:
        try:
            from net.Indyuce.mmoitems import MMOItems  # type: ignore
            IdParts = Parts[1].split(":")
            MMOItemsItem = MMOItems.plugin.getMMOItem(
                MMOItems.plugin.getTypes().get(IdParts[0]), IdParts[1]
                ).newBuilder().build()
            MMOItemsItem.setAmount(Amount)
            return MMOItemsItem
        except: return None
    else:
        try:
            Item = Material.valueOf(ItemType)
            return ItemStack(Item, Amount)
        except: return None

def GetItemIdentifier(Item):
    """获取物品的唯一标识符字符串
    
    参数:
        item: 物品对象
    
    返回:
        标识符字符串 (格式: "类型 标识符")
    """
    if CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            if CraftEngineItems.isCustomItem(Item):
                ItemID = CraftEngineItems.getCustomItemId(Item)
                return "craftengine " + str(ItemID)
        except: pass
    if MMOItemsAvailable:
        try:
            from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                return "mmoitems " + str(ItemType) + ":" + str(ItemId)
        except: pass
    return "minecraft " + Item.getType().name()

def IsToolItem(Item, Config, ToolType):
    """判断物品是否为指定的工具类型
    
    参数:
        item: 物品对象
        config: 配置对象
        tool_type: 工具类型 ("ChoppingBoard" 或 "Wok")
    
    返回:
        bool: 是否为指定工具
    """
    if not Item or Item.getType() == Material.AIR: return False
    if ToolType == "ChoppingBoard":
        CustomSetting = Config.getBoolean("Setting.ChoppingBoard.KitchenKnife.Custom")
        MaterialSetting = Config.getString("Setting.ChoppingBoard.KitchenKnife.Material")
    elif ToolType == "Wok":
        CustomSetting = Config.getBoolean("Setting.Wok.Spatula.Custom")
        MaterialSetting = Config.getString("Setting.Wok.Spatula.Material")
    else: return False
    if CustomSetting:
        if ' ' in MaterialSetting:
            Identifier, ID = MaterialSetting.split(' ', 1)
            if Identifier == "craftengine":
                if CraftEngineAvailable:
                    try:
                        from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
                        if CraftEngineItems.isCustomItem(Item):
                            ItemId = CraftEngineItems.getCustomItemId(Item)
                            return str(ItemId) == ID
                    except: pass
            elif Identifier == "mmoitems":
                if MMOItemsAvailable:
                    try:
                        from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
                        NbtItem = NBTItem.get(Item)
                        if NbtItem.hasType():
                            ItemType = NbtItem.getType()
                            ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                            CombinedId = str(ItemType) + ":" + str(ItemId)
                            return CombinedId == ID
                    except: pass
    else:
        try: return Item.getType() == Material.valueOf(MaterialSetting)
        except: pass
    return False

def OutputItemDisplayName(ItemStack):
    '''获取物品的显示名称
    
    参数
        Item: 物品栈 (ItemStack)
    返回
        str: 显示名称字符串
    '''
    if CraftEngineAvailable:
        from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
        from net.momirealms.craftengine.bukkit.item import BukkitItemManager  # type: ignore
        if CraftEngineItems.isCustomItem(ItemStack):
            Name = BukkitItemManager.instance().wrap(ItemStack).hoverNameJson().get()
            JsonData = json.loads(Name)
            return MiniMessage.miniMessage().deserialize(JsonData['text'])

    if MMOItemsAvailable:
        from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
        NbtItem = NBTItem.get(ItemStack)
        if NbtItem.hasType():
            return  MiniMessage.miniMessage().deserialize(ConvertLegacyColors(NbtItem.getString("MMOITEMS_NAME")))
             

    if ItemStack.hasDisplayName():
        return ItemStack.getDisplayName()
    return Component.translatable(ItemStack.translationKey())

ps.listener.registerListener(InteractionVanillaBlock, PlayerInteractEvent)
ps.listener.registerListener(BreakVanillaBlock, BlockBreakEvent)

def CommandExecute(sender, label, args):
    """处理/simplekitchen命令

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        命令执行结果
    """
    if args[0] == "reload":
        ReloadPlugin(sender)
        SendMessage(sender, LoadConfig().getString("Messages.Reload.LoadPlugin"))
    if isinstance(sender, Player):
        if args[0] == "clear":
            # 清除玩家周围半径3的展示实体
            for Entity in sender.getWorld().getNearbyEntities(sender.getLocation(), 0.5, 0.5, 0.5):
                if Entity.getType() == EntityType.ITEM_DISPLAY:
                    Entity.remove()
        elif args[0] == "test":
            HandItem = sender.getInventory().getItemInMainHand()
            sender.sendMessage(
                    Component.translatable(HandItem.translationKey()))
    return True

def ReloadPlugin(Target = Bukkit.getServer().getConsoleSender()):
    LoadConfig().reload()
    LoadChoppingBoardRecipe().reload()
    LoadData().reload()
    LoadWokRecipe().reload()
    ChoppingBoardRecipeAmount = LoadChoppingBoardRecipe().getKeys(False).size()
    WokRecipeAmount = LoadWokRecipe().getKeys(False).size()
    SendMessage(Target,LoadConfig()
                .getString("Messages.Reload.LoadChoppingBoardRecipe")
                .replace("{Amount}", str(ChoppingBoardRecipeAmount)))
    SendMessage(Target,LoadConfig()
                .getString("Messages.Reload.LoadWokRecipe")
                .replace("{Amount}", str(WokRecipeAmount)))

def Tab_CommandExecute(sender, label, args):
    """提供命令的补全建议

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        补全建议列表
    """
    if isinstance(sender, Player):
        return ["reload", "clear", "test"]
    return ["reload"]

# 注册命令
ps.command.registerCommand(CommandExecute, Tab_CommandExecute, "jiuwukitchen", ["jk"], "")

def ConvertLegacyColors(Message):
    """将传统颜色代码(&/§)转换为MiniMessage格式标签
    
    参数:
        Message: 包含传统颜色代码的字符串
        
    返回:
        转换后的MiniMessage兼容字符串
    """
    # 定义传统颜色代码到MiniMessage标签的映射
    LegacyToMiniMessage = {
        u'§0': u'<black>',
        u'§1': u'<dark_blue>',
        u'§2': u'<dark_green>',
        u'§3': u'<dark_aqua>',
        u'§4': u'<dark_red>',
        u'§5': u'<dark_purple>',
        u'§6': u'<gold>',
        u'§7': u'<gray>',
        u'§8': u'<dark_gray>',
        u'§9': u'<blue>',
        u'§a': u'<green>',
        u'§b': u'<aqua>',
        u'§c': u'<red>',
        u'§d': u'<light_purple>',
        u'§e': u'<yellow>',
        u'§f': u'<white>',
        u'§k': u'<obfuscated>',
        u'§l': u'<bold>',
        u'§m': u'<strikethrough>',
        u'§n': u'<underlined>',
        u'§o': u'<italic>',
        u'§r': u'<reset>',
    }
    for LegacyCode, MiniMessageTag in LegacyToMiniMessage.iteritems():
        Message = Message.replace(u"&", u"§").replace(LegacyCode, MiniMessageTag)
    return Message

def SendMessage(Target, Message):
    """向指定目标发送格式化消息（自动处理传统颜色代码）
    
    参数:
        Target: 消息接收者
        Message: 可能包含传统颜色代码的字符串
    """
    CleanMessage = ConvertLegacyColors(Message)
    MessagePrefix = LoadConfig().getString("Messages.Prefix")
    FormattedMessage = CleanMessage.replace(u"{Prefix}", MessagePrefix)
    Component = MiniMessage.miniMessage().deserialize(FormattedMessage)
    Target.sendMessage(Component)

def SendActionBar(Player, Message):
    """向玩家发送动作栏消息（自动处理传统颜色代码）
    
    参数:
        Player: 接收消息的玩家对象
        Message: 消息字符串（可能包含传统颜色代码）
    """
    CleanMessage = ConvertLegacyColors(Message)
    Component = MiniMessage.miniMessage().deserialize(CleanMessage)
    Player.sendActionBar(Component)

def SendSound(Player, Sound):
    """向玩家发送声音
    
    参数:
        Player: 接收声音的玩家对象
        Sound: 声音名称
    """
    try:
        Player.playSound(Player.getLocation(), Sound, 1, 1)
    except:
        return

def SendActionBarWithMaterial(Player, Message, MaterialComponent):
    """向玩家发送包含物品组件的动作栏消息
    
    参数:
        Player: 接收消息的玩家对象
        Message: 消息字符串 (包含{Material}占位符)
        MaterialComponent: 物品名称组件
    """
    Parts = Message.split("{Material}")
    Builder = Component.text()
    if Parts[0]:
        Builder.append(MiniMessage.miniMessage().deserialize(ConvertLegacyColors(Parts[0])))
    Builder.append(MaterialComponent)
    if len(Parts) > 1 and Parts[1]:
        Builder.append(MiniMessage.miniMessage().deserialize(ConvertLegacyColors(Parts[1])))
    Player.sendActionBar(Builder.build())

# 脚本启动检查
if ps.script.isScriptRunning("JiuWu's_Kitchen.py"):
    SendMessage(Bukkit.getServer().getConsoleSender(),
                LoadConfig().getString("Messages.Load").replace("{Version}", "v1.1"))
    SendMessage(Bukkit.getServer().getConsoleSender(),
                u"{Prefix} <red>Discord: <gray>https://discord.gg/jyhbPUkG")
    SendMessage(Bukkit.getServer().getConsoleSender(),
                u"{Prefix} <red>QQ群: <gray>299852340")
    ServerPluginLoad()
    ReloadPlugin()
