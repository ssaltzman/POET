package org.mitre.poet.model.lib;

import org.mitre.poet.model.*;

/**
 */
public class ModelCompiler {

    public InstanceDocument compilerModel(FilterDocument _filter, ConfigurationDocument _config, QuestionCorpusDocument _qa) {
        InstanceDocument id = generate_model(_filter, _config, _qa);

        return id;
    }

    protected InstanceDocument generate_model(FilterDocument filter, ConfigurationDocument config, QuestionCorpusDocument qa) {
        InstanceDocument id = InstanceDocument.Factory.newInstance();

        id = build_sample_document(id);

        return id;
    }

    protected InstanceDocument build_sample_document(InstanceDocument id) {
        InstanceType it = id.addNewInstance();

        it.setFilter("filter-1");
        it.setConfiguration("config-1");
        it.addNewVectors();

        VectorType vt = it.getVectors().addNewVector();
        vt.setName("trust");
        vt.setValue(95);
        VectorType.Pedigree pt = vt.addNewPedigree();

        pt.addQuestion("1");
        pt.addQuestion("2");
        pt.addQuestion("8");

        vt = it.getVectors().addNewVector();
        vt.setName("stakeholder commitment");
        vt.setValue(40);
        pt = vt.addNewPedigree();

        pt.addQuestion("6");
        pt.addQuestion("9");
        pt.addQuestion("2");


        vt = it.getVectors().addNewVector();
        vt.setName("agility");
        vt.setValue(5);
        pt = vt.addNewPedigree();

        pt.addQuestion("9");
        pt.addQuestion("1");
        pt.addQuestion("6");

        return id;
    }
}
