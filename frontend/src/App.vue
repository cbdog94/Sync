<template>
  <div id="app">
    <el-row>
      <!-- <el-container>
      <el-header>-->
      <el-col :span="24">
        <el-menu
          :default-active="$route.path"
          router
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
        >
          <el-col :span="12">
            <el-menu-item index="/sync">同步文字</el-menu-item>
          </el-col>
          <el-col :span="12">
            <el-menu-item index="/extract">提取文本</el-menu-item>
          </el-col>
        </el-menu>
      </el-col>
    </el-row>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeIndex: "1",
      syncData: {
        text: "",
        once: false
      }
    };
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath);
    }
  }
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
</style>
