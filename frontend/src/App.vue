<template>
  <el-row>
    <el-col :span="24">
      <el-menu
        :default-active="$route.path"
        router
        mode="horizontal"
        @select="handleSelect"
        :ellipsis="false"
      >
        <el-col :span="6">
          <el-menu-item index="/sync"><div class="menu-item-word">同步文字</div></el-menu-item>
        </el-col>
        <el-col :span="6">
          <el-menu-item index="/extract"><div class="menu-item-word">提取文本</div></el-menu-item>
        </el-col>
        <el-col :span="6">
          <el-menu-item index="/upload"><div class="menu-item-word">上传文件</div></el-menu-item>
        </el-col>
        <el-col :span="6">
          <el-menu-item index="/download"><div class="menu-item-word">提取文件</div></el-menu-item>
        </el-col>
      </el-menu>
    </el-col>
    <el-col :span="24">
      <router-view></router-view>
    </el-col>
  </el-row>
  
</template>

<script>
export default {
  data() {
    return {
      activeIndex: "1",
      syncData: {
        text: "",
        once: false,
      },
    };
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath);
    },
  },
};
</script>

<style>
#app {
  font-family: Helvetica, sans-serif;
  text-align: center;
}
body {
  margin: 0;
}
h4 {
  color: #303133;
}
.topmargin {
  margin-top: 20px;
}
.menu-item-word {
  width: 100%;
}
</style>
