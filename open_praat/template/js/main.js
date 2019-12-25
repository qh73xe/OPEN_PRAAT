new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    tab: 0,
    tab_items: ['Projects', 'Files', 'Edit Tool'],
    gui: {},
    tires: [],
    word: "",
    errors: "",
    is_snackbar_show: false,
    projects: [],
    project: "",
    filepath: [],
    current_files: {}
  },
  methods: {
    show_error: function(msg){
        this.errors = msg
        this.is_snackbar_show = true
    },
    init_projects: function(){
        eel.get_projects()((projects) => {
          this.projects = []
          for (const item of projects){
            this.projects.push(item)
          }
        })
    },
    set_project: function(text, val){
        this.project = text
        this.set_filepath(val)
        this.set_gui(val)
        this.tab = 1
    },
    set_filepath: function(val){
        eel.get_filepath(val)((res) => {
          this.filepath = []
          if (res.result){
            this.filepath = res.result.files
          } else {
            this.show_error(res.error)
          }
        })
    },
    set_gui: function(val){
        eel.get_gui(val)((res) => {
          this.gui = {}
          if (res.result){
            this.gui = res.result
            console.log(this.gui)
          } else {
            this.show_error(res.error)
          }
        })
    },
    open_praat: function(wav, tg){
        eel.open_praat(wav, tg)((res) => {
            this.current_files = res
            eel.get_tires(res.tg)((res) => {
                this.tires = res
            })
            this.tab = 2
        })
    },
    add_boundaly: function(tier){
        eel.add_boundaly(tier)((res) => {
            if (res == false){ this.show_error("Praat is not running!!") }
        })
    },
    add_word: function(tier, word){
        eel.add_word(tier, word)((res) => {
            if (res == false){ this.show_error("Praat is not running!!") }
        })
    },
    add_word_on_change: function(tier){
        if (this.word){
            this.add_word(tier, this.word)
            this.word = ""
        }
    },
    remove_boundaly: function(tier){
        eel.remove_boundaly(tier)((res) => {
            if (res == false){ this.show_error("Praat is not running!!") }
        })
    },
    save_textgrid: function(){
        eel.save_textgrid()((res) => {
            if (res == false){
                this.show_error("Praat is not running!!")
            } else {
                this.show_error(`SAVE ${this.current_files.tg}`)
            }
        })
    },
  },
  mounted: function() {
    this.init_projects()
  }
})
